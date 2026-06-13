class SearchService:
    """
    Unified search service using Hash Table for skills, Binary Search for experience.
    """
    
    def search_by_skill(self, skill_name: str) -> list:
        """Uses SkillSearchIndex (Hash Table) — O(1) lookup."""
        from search.indexes import skill_index
        skill_index.build()   # rebuild or use cache
        candidate_ids = skill_index.lookup(skill_name)
        from candidates.models import Candidate
        return list(Candidate.objects.filter(id__in=candidate_ids))
    
    def search_by_experience(self, min_exp: float, max_exp: float) -> list:
        """Uses ExperienceSearchIndex (Binary Search) — O(log n)."""
        from search.indexes import experience_index
        experience_index.build()
        candidate_ids = experience_index.search_range(min_exp, max_exp)
        from candidates.models import Candidate
        return list(Candidate.objects.filter(id__in=candidate_ids))
    
    def search_by_education(self, keyword: str) -> list:
        from candidates.models import Candidate
        return list(Candidate.objects.filter(education__icontains=keyword))
    
    def search_by_certification(self, cert_name: str) -> list:
        from candidates.models import Candidate
        return list(Candidate.objects.filter(
            certification__certificate_name__icontains=cert_name
        ).distinct())
    
    def combined_search(self, skill=None, min_exp=None, max_exp=None,
                        education=None, certification=None) -> list:
        """Combine all search criteria."""
        from candidates.models import Candidate
        qs = Candidate.objects.all()
        if skill:
            qs = qs.filter(candidateskill__skill__skill_name__icontains=skill)
        if min_exp is not None:
            qs = qs.filter(experience_years__gte=min_exp)
        if max_exp is not None:
            qs = qs.filter(experience_years__lte=max_exp)
        if education:
            qs = qs.filter(education__icontains=education)
        if certification:
            qs = qs.filter(certification__certificate_name__icontains=certification)
        return list(qs.distinct())
