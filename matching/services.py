class MatchingService:
    """
    Orchestrates the full matching pipeline for a job.
    Steps:
        1. Fetch all candidates
        2. For each candidate: run MatchingEngine (Greedy scoring)
        3. Collect all match dicts
        4. Run CandidateRanker (Merge Sort)
        5. Store all results in CandidateJobMatch table
        6. Run SkillGapAnalysis for each candidate
        7. Run SkillPathOptimizer (DP) for gap recommendations
    """
    
    def run_matching_for_job(self, job_id: int) -> dict:
        from jobs.models import Job
        from candidates.models import Candidate
        from matching.models import CandidateJobMatch, SkillGapAnalysis
        from matching.algorithms import MatchingEngine, CandidateRanker, SkillPathOptimizer
        from common.exceptions import JobNotFoundError
        
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            raise JobNotFoundError(f"Job ID {job_id} not found.")
        
        candidates = list(job.candidates.prefetch_related(
            'candidateskill_set__skill', 'certification_set'
        ).all())
        
        if not candidates:
            return {'message': 'No candidates in system.', 'total': 0}
        
        engine  = MatchingEngine()
        ranker  = CandidateRanker()
        gap_svc = SkillGapService()
        dp_opt  = SkillPathOptimizer()
        
        # Step 1: Calculate scores
        raw_matches = []
        for candidate in candidates:
            scores = engine.calculate_match(candidate, job)
            scores['candidate'] = candidate
            raw_matches.append(scores)
        
        # Step 2: Merge Sort — produce ranked list
        ranked = ranker.rank_candidates(raw_matches)
        
        # Step 3: Persist to database
        for match_data in ranked:
            candidate = match_data.pop('candidate')
            CandidateJobMatch.objects.update_or_create(
                candidate=candidate,
                job=job,
                defaults={
                    'skill_score':         match_data['skill_score'],
                    'experience_score':    match_data['experience_score'],
                    'certification_score': match_data['certification_score'],
                    'total_score':         match_data['total_score'],
                    'match_percentage':    match_data['match_percentage'],
                    'rank':                match_data['rank'],
                }
            )
            
            # Step 4: Skill Gap Analysis + DP path
            gap_result = gap_svc.analyze(candidate, job)
            missing = gap_result['missing_skills']
            missing_with_weights = [
                {'skill_name': s,
                 'weight': self._get_skill_weight(s, job)}
                for s in missing
            ]
            recommended_path = dp_opt.optimize(missing_with_weights, effort_budget=3)
            
            SkillGapAnalysis.objects.update_or_create(
                candidate=candidate,
                job=job,
                defaults={
                    'missing_skills':    missing,
                    'matched_skills':    gap_result['matched_skills'],
                    'readiness_score':   gap_result['readiness_score'],
                    'recommended_path':  recommended_path,
                }
            )
        
        return {
            'job_title':  job.title,
            'total_ranked': len(ranked),
            'top_candidate': ranked[0]['candidate'].name if ranked else None,
        }
    
    def _get_skill_weight(self, skill_name, job) -> float:
        from jobs.models import JobSkill
        try:
            return JobSkill.objects.get(
                job=job, skill__skill_name=skill_name
            ).weight
        except JobSkill.DoesNotExist:
            return 1.0


class SkillGapService:
    def analyze(self, candidate, job) -> dict:
        job_skill_names = set(
            js.skill.skill_name.lower()
            for js in job.jobskill_set.select_related('skill').all()
        )
        candidate_skill_names = set(
            cs.skill.skill_name.lower()
            for cs in candidate.candidateskill_set.select_related('skill').all()
        )
        matched  = list(job_skill_names & candidate_skill_names)
        missing  = list(job_skill_names - candidate_skill_names)
        readiness = (len(matched) / len(job_skill_names) * 100
                     if job_skill_names else 0.0)
        return {
            'matched_skills':  matched,
            'missing_skills':  missing,
            'readiness_score': round(readiness, 2),
        }
