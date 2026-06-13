from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView
from jobs.models import Job

class JobListView(ListView):
    model = Job
    template_name = 'hr/jobs/list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        return Job.objects.prefetch_related('jobskill_set__skill').order_by('-created_at')

class JobDetailView(DetailView):
    model = Job
    template_name = 'hr/jobs/detail.html'
    context_object_name = 'job'

class JobCreateView(View):
    template_name = 'hr/jobs/add.html'

    def get(self, request):
        from resume_processing.services import MASTER_SKILLS
        return render(request, self.template_name, {
            'all_skills': MASTER_SKILLS,
        })

    def post(self, request):
        from common.validators import JobValidator
        from jobs.models import Job, JobSkill
        from candidates.models import Skill
        
        post = request.POST
        try:
            JobValidator().validate_title(post.get('title'))
            JobValidator().validate_min_experience(post.get('min_experience'))
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('jobs:add')

        required_skills  = request.POST.getlist('required_skills')
        
        job = Job.objects.create(
            title=post['title'],
            description=post.get('description', ''),
            min_experience=float(post['min_experience']),
        )
        
        for s in required_skills:
            weight_key = f'weight_{s}'
            weight = float(post.get(weight_key, 1.0))
            skill_obj, _ = Skill.objects.get_or_create(skill_name=s, defaults={'category': 'Required'})
            JobSkill.objects.create(job=job, skill=skill_obj, weight=weight, is_required=True)

        messages.success(request, f'Job "{job.title}" created.')
        return redirect('jobs:detail', pk=job.pk)

class JobUploadView(View):
    template_name = 'hr/jobs/upload_jd.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        uploaded_file = request.FILES.get('jd_file')
        if not uploaded_file:
            messages.error(request, 'Please select a file.')
            return render(request, self.template_name)
        
        # Temporarily save and parse
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os
        from resume_processing.parsers import ParserFactory
        from resume_processing.services import SkillExtractor, ExperienceExtractor

        path = default_storage.save(
            f'jd_temp/{uploaded_file.name}',
            ContentFile(uploaded_file.read())
        )
        full_path = default_storage.path(path)
        
        try:
            parser = ParserFactory.get_parser(full_path)
            raw_text = parser.extract_text()
        finally:
            if os.path.exists(full_path):
                os.remove(full_path)
                
        # Simple extraction
        skills = SkillExtractor().extract(raw_text)
        exp = ExperienceExtractor().extract(raw_text)
        
        # Estimate a title (use file name without extension)
        import os
        base_name = os.path.basename(uploaded_file.name)
        title = os.path.splitext(base_name)[0]
        
        # Clean up the title (replace underscores/dashes with spaces, capitalize)
        title = title.replace('_', ' ').replace('-', ' ').title()
            
        request.session['extracted_jd'] = {
            'title': title,
            'description': raw_text[:2000], # Keep it manageable
            'min_experience': exp,
            'skills': [s['skill_name'] for s in skills]
        }
        
        return redirect('jobs:upload_confirm')

class JobUploadConfirmView(View):
    template_name = 'hr/jobs/confirm_jd.html'
    
    def get(self, request):
        extracted = request.session.get('extracted_jd')
        if not extracted:
            return redirect('jobs:upload')
            
        from resume_processing.services import MASTER_SKILLS
        return render(request, self.template_name, {
            'extracted': extracted,
            'all_skills': MASTER_SKILLS,
        })
        
    def post(self, request):
        # The user has confirmed, this mirrors JobCreateView logic
        from common.validators import JobValidator
        from jobs.models import Job, JobSkill
        from candidates.models import Skill
        
        post = request.POST
        try:
            JobValidator().validate_title(post.get('title'))
            JobValidator().validate_min_experience(post.get('min_experience'))
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('jobs:upload_confirm')

        required_skills  = request.POST.getlist('required_skills')
        
        job = Job.objects.create(
            title=post['title'],
            description=post.get('description', ''),
            min_experience=float(post['min_experience']),
        )
        
        for s in required_skills:
            weight_key = f'weight_{s}'
            weight = float(post.get(weight_key, 1.0))
            skill_obj, _ = Skill.objects.get_or_create(skill_name=s, defaults={'category': 'Required'})
            JobSkill.objects.create(job=job, skill=skill_obj, weight=weight, is_required=True)
            
        # Clean session
        if 'extracted_jd' in request.session:
            del request.session['extracted_jd']

        messages.success(request, f'Job "{job.title}" created from document.')
        return redirect('jobs:detail', pk=job.pk)

class JobAssignCandidatesView(View):
    template_name = 'hr/jobs/assign.html'

    def get(self, request, pk):
        from candidates.models import Candidate
        job = get_object_or_404(Job, pk=pk)
        all_candidates = Candidate.objects.all().order_by('-created_at')
        assigned_ids = job.candidates.values_list('id', flat=True)
        
        return render(request, self.template_name, {
            'job': job,
            'all_candidates': all_candidates,
            'assigned_ids': list(assigned_ids)
        })

    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        candidate_ids = request.POST.getlist('candidate_ids')
        
        # Clear existing and add new
        job.candidates.clear()
        if candidate_ids:
            job.candidates.add(*candidate_ids)
            
        messages.success(request, f'Successfully assigned {len(candidate_ids)} candidates to {job.title}.')
        return redirect('jobs:detail', pk=job.pk)

import csv
import io

class JobBulkUploadCandidatesView(View):
    template_name = 'hr/jobs/bulk_upload.html'
    
    def get(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return render(request, self.template_name, {'job': job})
        
    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please select a valid CSV file.')
            return render(request, self.template_name, {'job': job})
            
        try:
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string, None) # Skip header
            
            from candidates.models import Candidate, Skill, CandidateSkill, Certification
            
            count = 0
            for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                if len(row) < 6:
                    continue
                name, email, phone, education, exp, skills_str = row[:6]
                certs_str = row[6] if len(row) >= 7 else ""
                
                # Check if exists
                cand = Candidate.objects.filter(email=email).first()
                if not cand:
                    try:
                        exp = float(exp)
                    except ValueError:
                        exp = 0.0
                        
                    cand = Candidate.objects.create(
                        name=name.strip(),
                        email=email.strip(),
                        phone=phone.strip(),
                        education=education.strip(),
                        experience_years=exp,
                        resume_score=80.0
                    )
                    
                    for s_name in skills_str.split(','):
                        s_name = s_name.strip()
                        if s_name:
                            skill_obj, _ = Skill.objects.get_or_create(skill_name=s_name, defaults={'category': 'Bulk Imported'})
                            CandidateSkill.objects.create(candidate=cand, skill=skill_obj, proficiency_level='Intermediate')
                    
                    for c_name in certs_str.split(','):
                        c_name = c_name.strip()
                        if c_name:
                            Certification.objects.create(candidate=cand, certificate_name=c_name, issuer='Unknown')
                
                # Assign to job
                job.candidates.add(cand)
                count += 1
                
            messages.success(request, f'Successfully imported and assigned {count} candidates to {job.title}.')
            return redirect('jobs:detail', pk=job.pk)
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return render(request, self.template_name, {'job': job})
