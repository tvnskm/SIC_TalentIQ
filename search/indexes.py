class SkillSearchIndex:
    """
    Hash Table implementation for O(1) average skill lookup.
    Maps skill_name -> list of candidate_ids.
    Built once, queried many times.
    Demonstrates: Hash Table, Inverted Index concept.
    """
    
    def __init__(self):
        self._index: dict = {}    # The hash table: {skill_name: [candidate_ids]}
    
    def build(self):
        """Build the index from database. Call once at startup or after bulk import."""
        from candidates.models import CandidateSkill
        self._index = {}
        for cs in CandidateSkill.objects.select_related('skill', 'candidate').all():
            key = cs.skill.skill_name.lower()
            if key not in self._index:
                self._index[key] = []
            self._index[key].append(cs.candidate_id)
    
    def lookup(self, skill_name: str) -> list:
        """O(1) hash table lookup. Returns list of candidate IDs."""
        return self._index.get(skill_name.lower(), [])
    
    def get_all_skills(self) -> list:
        return list(self._index.keys())
    
    def add_candidate_skill(self, skill_name: str, candidate_id: int):
        """Incremental update — add single entry without full rebuild."""
        key = skill_name.lower()
        if key not in self._index:
            self._index[key] = []
        if candidate_id not in self._index[key]:
            self._index[key].append(candidate_id)

# Module-level singleton — build once, reuse everywhere
skill_index = SkillSearchIndex()

class ExperienceSearchIndex:
    """
    Binary Search implementation for experience-range queries.
    Maintains a sorted array of (experience_years, candidate_id) tuples.
    Time Complexity: O(log n) search after O(n log n) initial sort.
    Demonstrates: Binary Search on a sorted array.
    """
    
    def __init__(self):
        self._sorted_list: list = []   # [(experience_years, candidate_id), ...]
    
    def build(self):
        """Build sorted index from database."""
        from candidates.models import Candidate
        entries = list(Candidate.objects.values_list('experience_years', 'id'))
        self._sorted_list = sorted(entries, key=lambda x: x[0])
    
    def search_range(self, min_exp: float, max_exp: float) -> list:
        """
        Returns candidate IDs with experience in [min_exp, max_exp].
        Uses binary search to find the start and end positions.
        """
        left  = self._binary_search_left(min_exp)
        right = self._binary_search_right(max_exp)
        return [self._sorted_list[i][1] for i in range(left, right)]
    
    def _binary_search_left(self, target: float) -> int:
        """Find leftmost index where experience >= target."""
        lo, hi = 0, len(self._sorted_list)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._sorted_list[mid][0] < target:
                lo = mid + 1
            else:
                hi = mid
        return lo
    
    def _binary_search_right(self, target: float) -> int:
        """Find rightmost index where experience <= target."""
        lo, hi = 0, len(self._sorted_list)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._sorted_list[mid][0] <= target:
                lo = mid + 1
            else:
                hi = mid
        return lo

experience_index = ExperienceSearchIndex()
