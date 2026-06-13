from django.db import models
from candidates.models import Candidate
from jobs.models import Job

class CandidateJobMatch(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill_score = models.FloatField(default=0)
    experience_score = models.FloatField(default=0)
    certification_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)
    match_percentage = models.FloatField(default=0)
    rank = models.IntegerField(default=0)
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('candidate', 'job')

class SkillGapAnalysis(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    missing_skills = models.JSONField(default=list)      # list of skill names
    matched_skills = models.JSONField(default=list)      # list of skill names
    readiness_score = models.FloatField(default=0)
    recommended_path = models.JSONField(default=list)    # DP output — ordered learning path
    
    class Meta:
        unique_together = ('candidate', 'job')
