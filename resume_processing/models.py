from django.db import models
from candidates.models import Candidate

class Resume(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('PROCESSING', 'PROCESSING'),
        ('COMPLETED', 'COMPLETED'),
        ('FAILED', 'FAILED'),
    ]
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, null=True, blank=True)
    file_path = models.FileField(upload_to='resumes/')
    raw_text = models.TextField(blank=True)
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ProcessingQueue(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('PROCESSING', 'PROCESSING'),
        ('COMPLETED', 'COMPLETED'),
        ('FAILED', 'FAILED'),
    ]
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
