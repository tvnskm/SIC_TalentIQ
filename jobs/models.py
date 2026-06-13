from django.db import models
from candidates.models import Skill

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    min_experience = models.FloatField(default=0)
    candidates = models.ManyToManyField('candidates.Candidate', related_name='applied_jobs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    weight = models.FloatField(default=1.0)   # importance weight 0.0–2.0
    is_required = models.BooleanField(default=True)
