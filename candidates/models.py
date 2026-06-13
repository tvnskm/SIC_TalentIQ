from django.db import models

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    education = models.TextField()
    experience_years = models.FloatField(default=0)
    resume_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Skill(models.Model):
    skill_name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)  # e.g. Programming, Cloud, Data, Framework

class CandidateSkill(models.Model):
    PROFICIENCY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Expert', 'Expert'),
    ]
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=50, choices=PROFICIENCY_CHOICES)
    
    class Meta:
        unique_together = ('candidate', 'skill')

class Certification(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    certificate_name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    issue_date = models.DateField(null=True, blank=True)
