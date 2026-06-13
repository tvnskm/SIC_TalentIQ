from resume_processing.parsers import ParserFactory
from resume_processing.services import (
    SkillExtractor, EducationExtractor,
    ExperienceExtractor, CertificationExtractor
)
from jobs.models import Job, JobSkill
from matching.algorithms import GreedySkillMatcher, SkillPathOptimizer
from .models import PortalSession

class PortalResumeService:
    
    def process_upload(self, uploaded_file) -> PortalSession:
        """Parse resume → extract → store in PortalSession (not Candidate)."""
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import os

        # Temp save for parsing
        path = default_storage.save(
            f'portal_temp/{uploaded_file.name}',
            ContentFile(uploaded_file.read())
        )
        full_path = default_storage.path(path)

        try:
            parser   = ParserFactory.get_parser(full_path)
            raw_text = parser.extract_text()
        finally:
            # Always delete temp file — no permanent storage
            if os.path.exists(full_path):
                os.remove(full_path)

        skills   = SkillExtractor().extract(raw_text)
        edu      = EducationExtractor().extract(raw_text)
        exp      = ExperienceExtractor().extract(raw_text)
        certs    = CertificationExtractor().extract(raw_text)
        score    = self._calculate_score(skills, exp, certs)
        matches  = self._match_against_jobs(skills, exp)

        session = PortalSession.objects.create(
            raw_resume_text  = raw_text,
            extracted_skills = [s['skill_name'] for s in skills],
            education        = edu,
            experience_years = exp,
            certifications   = certs,
            resume_score     = score,
            job_matches      = matches,
        )
        return session

    def _calculate_score(self, skills, exp_years, certs) -> float:
        skill_score = min(len(skills) * 5, 60)
        exp_score   = min(exp_years * 3, 25)
        cert_score  = min(len(certs) * 5, 15)
        return round(skill_score + exp_score + cert_score, 2)

    def _match_against_jobs(self, skills, exp_years) -> list:
        """Read-only scan of all active jobs. Returns top matches."""
        skill_names = set(s['skill_name'].lower() for s in skills)
        results     = []

        for job in Job.objects.prefetch_related('jobskill_set__skill').all():
            job_skills = list(job.jobskill_set.select_related('skill').all())
            if not job_skills:
                continue
            matched   = [js for js in job_skills
                         if js.skill.skill_name.lower() in skill_names]
            readiness = round(len(matched) / len(job_skills) * 100, 2)

            # Skill gap for this job
            missing = [js.skill.skill_name for js in job_skills
                       if js.skill.skill_name.lower() not in skill_names]
            # DP path
            missing_w = [{'skill_name': js.skill.skill_name,
                          'weight': js.weight}
                         for js in job_skills
                         if js.skill.skill_name.lower() not in skill_names]
            dp_path = SkillPathOptimizer().optimize(missing_w, effort_budget=3)

            results.append({
                'job_id':       job.id,
                'job_title':    job.title,
                'readiness':    readiness,
                'matched':      [js.skill.skill_name for js in matched],
                'missing':      missing,
                'dp_path':      dp_path,
                'exp_ok':       exp_years >= job.min_experience,
            })

        return sorted(results, key=lambda x: x['readiness'], reverse=True)[:5]

    def get_improvement_suggestions(self, session: PortalSession) -> list:
        """Rule-based resume improvement suggestions."""
        suggestions = []
        if session.experience_years == 0:
            suggestions.append({
                'type':    'warning',
                'message': 'Add years of experience to improve job matching accuracy.'
            })
        if len(session.extracted_skills) < 5:
            suggestions.append({
                'type':    'warning',
                'message': 'Your resume lists fewer than 5 skills. '
                           'Add more technical skills explicitly.'
            })
        if not session.certifications:
            suggestions.append({
                'type':    'info',
                'message': 'Adding certifications (AWS, PMP, etc.) '
                           'can boost your match score by up to 15 points.'
            })
        if not session.education:
            suggestions.append({
                'type':    'warning',
                'message': 'No education details detected. '
                           'Ensure your degree is clearly stated.'
            })
        if session.resume_score >= 70:
            suggestions.append({
                'type':    'success',
                'message': 'Your resume score is strong. '
                           'Focus on applying for jobs where readiness > 60%.'
            })
        return suggestions
