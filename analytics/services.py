import pandas as pd
import numpy as np
from candidates.models import Candidate, CandidateSkill, Certification
from matching.models import CandidateJobMatch
from jobs.models import Job

class AnalyticsService:
    
    def get_dashboard_summary(self) -> dict:
        total_candidates = Candidate.objects.count()
        total_jobs = Job.objects.count()
        
        match_scores = list(CandidateJobMatch.objects.values_list('total_score', flat=True))
        avg_match = round(np.mean(match_scores), 2) if match_scores else 0
        
        top_match = CandidateJobMatch.objects.order_by('-total_score').first()
        top_candidate = top_match.candidate.name if top_match else "N/A"
        
        return {
            'total_candidates': total_candidates,
            'total_jobs': total_jobs,
            'average_match_score': float(avg_match),
            'top_ranked_candidate': top_candidate,
        }
    
    def get_experience_statistics(self) -> dict:
        """NumPy statistical analysis on experience data."""
        data = list(Candidate.objects.values_list('experience_years', flat=True))
        if not data:
            return {}
        arr = np.array(data, dtype=float)
        df = pd.DataFrame({'experience_years': arr})
        
        # Distribution buckets using Pandas cut
        bins = [0, 2, 5, 8, 12, 100]
        labels = ['0-2 yrs', '3-5 yrs', '6-8 yrs', '9-12 yrs', '12+ yrs']
        df['bucket'] = pd.cut(df['experience_years'], bins=bins, labels=labels, right=False)
        distribution = df['bucket'].value_counts().sort_index().to_dict()
        distribution = {str(k): int(v) for k, v in distribution.items()}
        
        return {
            'mean':         round(float(np.mean(arr)), 2),
            'median':       round(float(np.median(arr)), 2),
            'std_dev':      round(float(np.std(arr)), 2),
            'percentile_25': round(float(np.percentile(arr, 25)), 2),
            'percentile_75': round(float(np.percentile(arr, 75)), 2),
            'min':          round(float(np.min(arr)), 2),
            'max':          round(float(np.max(arr)), 2),
            'distribution': distribution,
        }
    
    def get_top_skills(self, top_n: int = 10) -> list:
        """Pandas value_counts on skill frequency across all candidates."""
        data = list(CandidateSkill.objects.select_related('skill')
                    .values_list('skill__skill_name', flat=True))
        if not data:
            return []
        df = pd.DataFrame({'skill': data})
        counts = df['skill'].value_counts().head(top_n)
        return [{'skill': str(k), 'count': int(v)} for k, v in counts.items()]
    
    def get_education_distribution(self) -> dict:
        """Pandas groupby on education field parsed for keywords."""
        data = list(Candidate.objects.values_list('education', flat=True))
        if not data:
            return {}
        
        def classify(edu):
            edu_lower = str(edu).lower()
            if 'phd' in edu_lower or 'doctorate' in edu_lower:
                return 'PhD'
            elif 'master' in edu_lower or 'msc' in edu_lower or 'mba' in edu_lower:
                return 'Masters'
            elif 'bachelor' in edu_lower or 'bsc' in edu_lower or 'be ' in edu_lower:
                return 'Bachelors'
            elif 'diploma' in edu_lower:
                return 'Diploma'
            else:
                return 'Other'
        
        df = pd.DataFrame({'education': data})
        df['level'] = df['education'].apply(classify)
        counts = df['level'].value_counts().to_dict()
        return {str(k): int(v) for k, v in counts.items()}
    
    def get_match_score_distribution(self) -> dict:
        """Pandas + NumPy histogram on match percentages."""
        scores = list(CandidateJobMatch.objects.values_list('match_percentage', flat=True))
        if not scores:
            return {}
        arr = np.array(scores, dtype=float)
        df = pd.DataFrame({'score': arr})
        bins = [0, 20, 40, 60, 80, 100]
        labels = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
        df['bucket'] = pd.cut(df['score'], bins=bins, labels=labels)
        counts = df['bucket'].value_counts().sort_index().to_dict()
        return {str(k): int(v) for k, v in counts.items()}
    
    def get_certification_distribution(self) -> dict:
        """Count of certifications per candidate using Pandas groupby."""
        data = list(Certification.objects.values_list('candidate_id', flat=True))
        if not data:
            return {'0 certs': Candidate.objects.count()}
        df = pd.DataFrame({'candidate_id': data})
        counts = df['candidate_id'].value_counts()
        distribution = counts.value_counts().to_dict()
        return {f'{k} cert(s)': int(v) for k, v in sorted(distribution.items())}

    def get_top_ranked_candidates(self, top_n: int = 10) -> list:
        matches = CandidateJobMatch.objects.select_related('candidate', 'job').order_by('-match_percentage')[:top_n]
        return [
            {
                'rank': i + 1,
                'candidate_id': m.candidate.id,
                'candidate_name': m.candidate.name,
                'job_title': m.job.title,
                'match_percentage': m.match_percentage
            }
            for i, m in enumerate(matches)
        ]

    def get_job_specific_analytics(self, job_id: int) -> dict:
        """Returns JSON-serializable dictionaries for Chart.js rendering."""
        matches = CandidateJobMatch.objects.filter(job_id=job_id).select_related('candidate')
        if not matches.exists():
            return {'top_skills': {}, 'experience_distribution': {}, 'match_distribution': {}}
            
        candidate_ids = matches.values_list('candidate_id', flat=True)
        
        # 1. Top Skills Demanded vs Available
        from jobs.models import JobSkill
        job_skills = list(JobSkill.objects.filter(job_id=job_id).values_list('skill__skill_name', flat=True))
        
        if job_skills:
            # Count how many assigned candidates have the specific demanded skills
            skills = list(CandidateSkill.objects.filter(
                candidate_id__in=candidate_ids, 
                skill__skill_name__in=job_skills
            ).values_list('skill__skill_name', flat=True))
            
            top_skills = {skill_name: 0 for skill_name in job_skills}
            if skills:
                df_skills = pd.DataFrame({'skill': skills})
                counts = df_skills['skill'].value_counts().to_dict()
                for k, v in counts.items():
                    top_skills[str(k)] = int(v)
        else:
            # Fallback if job has no required skills defined
            skills = list(CandidateSkill.objects.filter(candidate_id__in=candidate_ids)
                          .values_list('skill__skill_name', flat=True))
            top_skills = {}
            if skills:
                df_skills = pd.DataFrame({'skill': skills})
                counts = df_skills['skill'].value_counts().head(10)
                top_skills = {str(k): int(v) for k, v in counts.items()}
            
        # 2. Experience Distribution
        exp_data = list(Candidate.objects.filter(id__in=candidate_ids)
                        .values_list('experience_years', flat=True))
        exp_dist = {}
        if exp_data:
            df_exp = pd.DataFrame({'experience': np.array(exp_data, dtype=float)})
            bins = [0, 2, 5, 8, 100]
            labels = ['0-2 yrs', '3-5 yrs', '6-8 yrs', '9+ yrs']
            df_exp['bucket'] = pd.cut(df_exp['experience'], bins=bins, labels=labels, right=False)
            dist = df_exp['bucket'].value_counts().sort_index().to_dict()
            exp_dist = {str(k): int(v) for k, v in dist.items()}
            
        # 3. Match Score Distribution
        scores = list(matches.values_list('match_percentage', flat=True))
        match_dist = {}
        if scores:
            df_scores = pd.DataFrame({'score': np.array(scores, dtype=float)})
            bins = [0, 40, 70, 100]
            labels = ['Low (0-40%)', 'Medium (41-70%)', 'High (71-100%)']
            df_scores['bucket'] = pd.cut(df_scores['score'], bins=bins, labels=labels, right=True)
            dist = df_scores['bucket'].value_counts().sort_index().to_dict()
            match_dist = {str(k): int(v) for k, v in dist.items()}
            
        return {
            'top_skills': top_skills,
            'experience_distribution': exp_dist,
            'match_distribution': match_dist
        }
