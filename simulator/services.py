from matching.algorithms import GreedySkillMatcher, CandidateRanker, MatchingEngine

class SimulatorService:
    """
    In-memory matching with custom weights.
    Does NOT touch CandidateJobMatch table.
    Returns temporary rankings for display only.
    """

    def simulate(self, job_id: int, custom_weights: dict,
                 exp_weight: float = 0.20,
                 cert_weight: float = 0.10) -> list:
        """
        custom_weights: {'Python': 2.0, 'AWS': 1.5, 'SQL': 1.0, ...}
        These override the stored JobSkill.weight values temporarily.
        """
        from jobs.models import Job, JobSkill
        from candidates.models import Candidate

        job        = Job.objects.get(pk=job_id)
        candidates = list(Candidate.objects.prefetch_related(
            'candidateskill_set__skill', 'certification_set'
        ).all())

        skill_weight_total = 1.0 - exp_weight - cert_weight

        raw_matches = []
        for candidate in candidates:
            skill_score  = self._greedy_with_custom_weights(
                               candidate, job, custom_weights)
            exp_score    = self._exp_score(candidate, job)
            cert_score   = self._cert_score(candidate)

            total = (skill_score  * skill_weight_total +
                     exp_score    * exp_weight +
                     cert_score   * cert_weight)

            raw_matches.append({
                'candidate_id':   candidate.id,
                'candidate_name': candidate.name,
                'skill_score':    round(skill_score, 2),
                'exp_score':      round(exp_score, 2),
                'cert_score':     round(cert_score, 2),
                'total_score':    round(total, 2),
            })

        # Merge sort (same DSA class, reused)
        ranked = CandidateRanker().rank_candidates(raw_matches)
        return ranked

    def _greedy_with_custom_weights(self, candidate, job, custom_weights) -> float:
        job_skills = list(job.jobskill_set.select_related('skill').all())
        if not job_skills:
            return 0.0
        cand_skills = set(
            cs.skill.skill_name.lower()
            for cs in candidate.candidateskill_set.select_related('skill').all()
        )
        total_weight  = 0.0
        earned_weight = 0.0
        for js in sorted(job_skills,
                         key=lambda x: custom_weights.get(x.skill.skill_name,
                                                          x.weight),
                         reverse=True):
            w = custom_weights.get(js.skill.skill_name, js.weight)
            total_weight += w
            if js.skill.skill_name.lower() in cand_skills:
                earned_weight += w
        return (earned_weight / total_weight * 100) if total_weight else 0.0

    def _exp_score(self, candidate, job) -> float:
        if job.min_experience == 0:
            return 100.0
        return min((candidate.experience_years / job.min_experience) * 100, 100)

    def _cert_score(self, candidate) -> float:
        return min(candidate.certification_set.count() * 25, 100)
