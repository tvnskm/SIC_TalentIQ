from abc import ABC, abstractmethod

class CandidateRanker:
    """
    Implements Merge Sort to rank candidates by total_score.
    Time Complexity: O(n log n)
    Demonstrates: Divide and Conquer, Recursive Algorithm
    NOTE: This is an explicit Python implementation — NOT Django ORM ordering.
    """
    
    def rank_candidates(self, matches: list) -> list:
        """
        Entry point. matches = list of dicts with 'total_score' key.
        Returns sorted list descending by total_score with rank assigned.
        """
        sorted_matches = self._merge_sort(matches)
        for i, match in enumerate(sorted_matches):
            match['rank'] = i + 1
        return sorted_matches
    
    def _merge_sort(self, arr: list) -> list:
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left  = self._merge_sort(arr[:mid])
        right = self._merge_sort(arr[mid:])
        return self._merge(left, right)
    
    def _merge(self, left: list, right: list) -> list:
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            # Descending order — higher score = better rank
            if left[i]['total_score'] >= right[j]['total_score']:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

class GreedySkillMatcher:
    """
    Greedy Algorithm for skill-based scoring.
    Strategy: Always match the highest-weighted job skill first.
    This maximises the score achieved per skill matched.
    Time Complexity: O(n log n) due to sorting by weight.
    Demonstrates: Greedy Algorithm — always take the locally optimal choice.
    """
    
    def match(self, candidate, job) -> float:
        # Get job skills sorted by weight descending (greedy order)
        job_skills = list(
            job.jobskill_set.select_related('skill')
                            .order_by('-weight')
        )
        if not job_skills:
            return 0.0
        
        candidate_skill_names = set(
            cs.skill.skill_name.lower()
            for cs in candidate.candidateskill_set.select_related('skill').all()
        )
        
        total_weight = sum(js.weight for js in job_skills)
        earned_weight = 0.0
        
        # Greedy match: iterate skills in weight order, take match if available
        for job_skill in job_skills:
            skill_name = job_skill.skill.skill_name.lower()
            if skill_name in candidate_skill_names:
                earned_weight += job_skill.weight   # greedy take
        
        if total_weight == 0:
            return 0.0
        return round((earned_weight / total_weight) * 100, 2)

class SkillPathOptimizer:
    """
    DYNAMIC PROGRAMMING — 0/1 Knapsack variant.

    Problem: Given a candidate's missing skills for a job,
    and a configurable "effort budget" (number of skills they can learn),
    find the set of skills to learn that maximises job requirement coverage.

    This directly produces a "Recommended Learning Path" for each candidate.

    Parameters:
        missing_skills: list of dicts [{skill_name, weight}]
        effort_budget:  max number of skills candidate can learn (default 3)

    Returns:
        List of skill names in recommended learning order (highest impact first)

    Time Complexity: O(n × W) where n=skills, W=budget
    Space Complexity: O(n × W)
    Demonstrates: Dynamic Programming, Optimal Substructure, Overlapping Subproblems
    """
    
    def optimize(self, missing_skills: list, effort_budget: int = 3) -> list:
        if not missing_skills:
            return []
        
        n = len(missing_skills)
        W = effort_budget
        
        # Each skill costs 1 unit of effort, value = job requirement weight
        weights = [1] * n                               # cost to learn each skill
        values  = [s.get('weight', 1.0) for s in missing_skills]  # job importance
        
        # Build DP table — dp[i][w] = max value using first i items with budget w
        dp = [[0.0] * (W + 1) for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            for w in range(W + 1):
                # Don't learn skill i-1
                dp[i][w] = dp[i-1][w]
                # Learn skill i-1 if budget allows
                if weights[i-1] <= w:
                    val_if_taken = dp[i-1][w - weights[i-1]] + values[i-1]
                    if val_if_taken > dp[i][w]:
                        dp[i][w] = val_if_taken
        
        # Backtrack to find which skills were selected
        selected = []
        w = W
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selected.append(missing_skills[i-1]['skill_name'])
                w -= weights[i-1]
        
        # Return in descending value order (highest impact first)
        selected_with_value = [
            (s, next(m['weight'] for m in missing_skills if m['skill_name'] == s))
            for s in selected
        ]
        selected_with_value.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in selected_with_value]

class BaseScorer(ABC):
    """Abstract scorer — OOP base for all scoring strategies"""
    @abstractmethod
    def calculate(self, candidate, job) -> float:
        pass
    
    def normalize(self, score: float) -> float:
        return max(0.0, min(100.0, score))


class SkillScorer(BaseScorer):
    """Scores candidate based on skill match using Greedy algorithm"""
    def calculate(self, candidate, job) -> float:
        return GreedySkillMatcher().match(candidate, job)


class ExperienceScorer(BaseScorer):
    """Scores candidate based on experience vs job requirement"""
    def calculate(self, candidate, job) -> float:
        if job.min_experience == 0:
            return 100.0
        ratio = candidate.experience_years / job.min_experience
        return self.normalize(ratio * 100)


class CertificationScorer(BaseScorer):
    """Scores candidate based on number of certifications"""
    def calculate(self, candidate, job) -> float:
        cert_count = candidate.certification_set.count()
        if cert_count == 0:
            return 0.0
        return self.normalize(min(cert_count * 25, 100))


class MatchingEngine:
    """
    Composition pattern — uses multiple scorer objects.
    Demonstrates: Composition over Inheritance, Strategy Pattern
    Weights: Skill 70%, Experience 20%, Certification 10%
    """
    WEIGHTS = {
        'skill':         0.70,
        'experience':    0.20,
        'certification': 0.10,
    }
    
    def __init__(self):
        self._scorers = {
            'skill':         SkillScorer(),
            'experience':    ExperienceScorer(),
            'certification': CertificationScorer(),
        }
    
    def calculate_match(self, candidate, job) -> dict:
        scores = {k: scorer.calculate(candidate, job)
                  for k, scorer in self._scorers.items()}
        
        total = sum(scores[k] * self.WEIGHTS[k] for k in scores)
        
        return {
            'skill_score':         round(scores['skill'], 2),
            'experience_score':    round(scores['experience'], 2),
            'certification_score': round(scores['certification'], 2),
            'total_score':         round(total, 2),
            'match_percentage':    round(total, 2),
        }
