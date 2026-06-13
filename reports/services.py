import csv
import json
import io
from candidates.models import Candidate, CandidateSkill, Certification
from matching.models import CandidateJobMatch, SkillGapAnalysis

class ReportService:
    
    def export_candidates_csv(self) -> str:
        """Returns CSV string of all candidates."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID','Name','Email','Phone','Education',
                         'Experience (yrs)','Resume Score','Skills','Created At'])
        for c in Candidate.objects.prefetch_related('candidateskill_set__skill').all():
            skills = ', '.join(cs.skill.skill_name
                               for cs in c.candidateskill_set.all())
            writer.writerow([
                c.id, c.name, c.email, c.phone,
                c.education, c.experience_years,
                c.resume_score, skills, c.created_at.date()
            ])
        return output.getvalue()
    
    def export_rankings_json(self, job_id=None) -> str:
        """Returns JSON string of all rankings, optionally filtered by job."""
        qs = CandidateJobMatch.objects.select_related('candidate','job')
        if job_id:
            qs = qs.filter(job_id=job_id)
        data = [
            {
                'rank':             m.rank,
                'candidate_id':     m.candidate.id,
                'candidate_name':   m.candidate.name,
                'job_id':           m.job.id,
                'job_title':        m.job.title,
                'skill_score':      m.skill_score,
                'experience_score': m.experience_score,
                'cert_score':       m.certification_score,
                'total_score':      m.total_score,
                'match_percentage': m.match_percentage,
            }
            for m in qs.order_by('job_id', 'rank')
        ]
        return json.dumps(data, indent=2)
    
    def export_skill_gap_csv(self) -> str:
        """Returns CSV of skill gap analysis for all candidate-job pairs."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Candidate','Job','Matched Skills','Missing Skills',
                         'Readiness Score (%)','Recommended Learning Path'])
        for gap in SkillGapAnalysis.objects.select_related('candidate','job').all():
            writer.writerow([
                gap.candidate.name,
                gap.job.title,
                ', '.join(gap.matched_skills),
                ', '.join(gap.missing_skills),
                gap.readiness_score,
                ' → '.join(gap.recommended_path),
            ])
        return output.getvalue()
    
    def export_analytics_csv(self, analytics_service) -> str:
        """Returns analytics summary as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Skills section
        writer.writerow(['TOP SKILLS'])
        writer.writerow(['Skill', 'Count'])
        for row in analytics_service.get_top_skills():
            writer.writerow([row['skill'], row['count']])
        
        writer.writerow([])
        
        # Experience section
        stats = analytics_service.get_experience_statistics()
        writer.writerow(['EXPERIENCE STATISTICS'])
        writer.writerow(['Metric', 'Value'])
        for k, v in stats.items():
            if k != 'distribution':
                writer.writerow([k, v])
        
        return output.getvalue()
