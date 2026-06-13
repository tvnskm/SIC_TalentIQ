from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .parsers import ParserFactory
from .parsers import ParserFactory
from .services import SkillExtractor, EducationExtractor, ExperienceExtractor, CertificationExtractor, NameExtractor, EmailExtractor, PhoneExtractor
from .queue_service import ResumeQueueService
from .models import Resume
from common.validators import ResumeValidator
from common.exceptions import InvalidFileFormatError, FileSizeTooLargeError

class ResumeUploadView(View):
    template_name = 'hr/resume/upload.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        uploaded_file = request.FILES.get('resume_file')
        if not uploaded_file:
            messages.error(request, 'Please select a file.')
            return render(request, self.template_name)

        # ── Validate (common/validators.py) ──
        try:
            ResumeValidator().validate(uploaded_file)
        except (InvalidFileFormatError, FileSizeTooLargeError) as e:
            messages.error(request, str(e))
            return render(request, self.template_name)

        # ── Save file (status=PENDING, no candidate yet) ──
        resume = Resume.objects.create(
            file_path=uploaded_file,
            processing_status='PENDING'
        )

        # ── Enqueue (Queue DSA) ──
        ResumeQueueService().enqueue(resume.id)

        # ── Process immediately (for demo: sync) ──
        self._process_resume(resume)

        return redirect('resumes:preview', pk=resume.pk)

    def _process_resume(self, resume):
        """Parse → extract → store raw text. No candidate saved yet."""
        try:
            resume.processing_status = 'PROCESSING'
            resume.save()
            parser = ParserFactory.get_parser(resume.file_path.path)
            raw_text = parser.extract_text()
            resume.raw_text = raw_text
            resume.processing_status = 'COMPLETED'
            resume.save()
        except Exception as e:
            resume.processing_status = 'FAILED'
            resume.save()


class ResumePreviewView(View):
    template_name = 'hr/resume/preview.html'

    def get(self, request, pk):
        resume = get_object_or_404(Resume, pk=pk)
        if resume.processing_status != 'COMPLETED':
            messages.warning(request, 'Resume is still processing.')
            return redirect('resumes:upload')

        text = resume.raw_text

        # ── Run all extractors ──
        extracted = {
            'name':           NameExtractor().extract(text),
            'email':          EmailExtractor().extract(text),
            'phone':          PhoneExtractor().extract(text),
            'skills':         SkillExtractor().extract(text),
            'education':      EducationExtractor().extract(text),
            'experience':     ExperienceExtractor().extract(text),
            'certifications': CertificationExtractor().extract(text),
            'raw_text':       text,
        }

        # ── Pass all master skills for the checkbox UI ──
        from resume_processing.services import MASTER_SKILLS
        return render(request, self.template_name, {
            'resume':       resume,
            'extracted':    extracted,
            'all_skills':   MASTER_SKILLS,
        })


class ResumeConfirmView(View):
    """POST only. Saves confirmed data as a real Candidate."""

    def post(self, request, pk):
        resume = get_object_or_404(Resume, pk=pk)
        
        # Need CandidateCreationService which hasn't been implemented yet, let's implement a simplified version here
        # that handles creation inline.
        from common.validators import CandidateValidator
        from common.exceptions import DuplicateCandidateError
        from candidates.models import Candidate, Skill, CandidateSkill, Certification

        post = request.POST

        try:
            CandidateValidator().validate_email(post.get('email', ''))
            CandidateValidator().validate_experience(post.get('experience_years', 0))
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('resumes:preview', pk=pk)

        confirmed_skills = request.POST.getlist('skills')  # checkboxes
        confirmed_certs  = request.POST.getlist('certifications')

        email = post.get('email')
        if Candidate.objects.filter(email=email).exists():
            messages.error(request, f"Candidate with email {email} already exists.")
            return redirect('resumes:preview', pk=pk)

        candidate = Candidate.objects.create(
            name=post.get('name'),
            email=email,
            phone=post.get('phone', ''),
            education=post.get('education', ''),
            experience_years=float(post.get('experience_years', 0)),
            resume_score=75.0 # default dummy score
        )
        
        resume.candidate = candidate
        resume.save()

        # Save Skills
        for skill_name in confirmed_skills:
            skill_obj, _ = Skill.objects.get_or_create(skill_name=skill_name, defaults={'category': 'Extracted'})
            CandidateSkill.objects.create(candidate=candidate, skill=skill_obj, proficiency_level='Intermediate')
            
        # Save Certs
        for cert in confirmed_certs:
            if cert.strip():
               # Clean up session
                if 'extracted_data' in request.session:
                    del request.session['extracted_data']
            
        messages.success(request, f'Candidate {candidate.name} created successfully.')
        return redirect('candidates:detail', pk=candidate.pk)

class ResumeBulkUploadView(View):
    template_name = 'hr/resume/bulk_upload.html'
    
    def get(self, request):
        return render(request, self.template_name)
        
    def post(self, request):
        uploaded_files = request.FILES.getlist('resumes')
        if not uploaded_files:
            messages.error(request, 'Please select at least one resume file.')
            return render(request, self.template_name)
            
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os
        import os
        from resume_processing.parsers import ParserFactory
        from resume_processing.services import SkillExtractor, ExperienceExtractor, EducationExtractor, CertificationExtractor, NameExtractor, EmailExtractor, PhoneExtractor
        from candidates.models import Candidate, Skill, CandidateSkill, Certification
        
        count = 0
        for uploaded_file in uploaded_files:
            # 1. Temporarily save file
            path = default_storage.save(
                f'bulk_temp/{uploaded_file.name}',
                ContentFile(uploaded_file.read())
            )
            full_path = default_storage.path(path)
            
            try:
                # 2. Extract Text
                parser = ParserFactory.get_parser(full_path)
                raw_text = parser.extract_text()
                
                # 3. Use AI Extractors
                skills = SkillExtractor().extract(raw_text)
                exp = ExperienceExtractor().extract(raw_text)
                edu = EducationExtractor().extract(raw_text)
                certs = CertificationExtractor().extract(raw_text)
                
                # Extract contact details
                ext_name = NameExtractor().extract(raw_text)
                ext_email = EmailExtractor().extract(raw_text)
                ext_phone = PhoneExtractor().extract(raw_text)
                
                # Fallback to filename if extraction is weird
                if not ext_name or len(ext_name) < 2:
                    ext_name = os.path.splitext(os.path.basename(uploaded_file.name))[0].replace('_', ' ').replace('-', ' ').title()
                
                if not ext_email:
                    ext_email = f"{ext_name.replace(' ', '').lower()}@example.com"
                
                # Create Candidate
                cand = Candidate.objects.create(
                    name=ext_name,
                    email=ext_email,
                    phone=ext_phone if ext_phone else "Not specified",
                    education=edu,
                    experience_years=exp,
                    resume_score=85.0
                )
                
                # Attach Skills
                for s in skills:
                    skill_obj, _ = Skill.objects.get_or_create(skill_name=s['skill_name'], defaults={'category': s['category']})
                    CandidateSkill.objects.create(candidate=cand, skill=skill_obj, proficiency_level='Intermediate')
                    
                # Attach Certifications
                for c in certs:
                    Certification.objects.create(candidate=cand, certificate_name=c, issuer='Unknown')
                    
                count += 1
            except Exception as e:
                # Just skip failing files
                print(f"Failed to process {uploaded_file.name}: {str(e)}")
            finally:
                if os.path.exists(full_path):
                    os.remove(full_path)
                    
        messages.success(request, f'Successfully parsed and imported {count} resumes.')
        return redirect('candidates:list')
