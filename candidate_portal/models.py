import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta

class PortalSession(models.Model):
    """
    Temporary record for candidate portal usage.
    Expires after 24 hours. Never touches Candidate model.
    Cleaned up by management command: python manage.py cleanup_sessions
    """
    session_key       = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    raw_resume_text   = models.TextField(blank=True)
    extracted_skills  = models.JSONField(default=list)
    education         = models.CharField(max_length=500, blank=True)
    experience_years  = models.FloatField(default=0)
    certifications    = models.JSONField(default=list)
    resume_score      = models.FloatField(default=0)
    job_matches       = models.JSONField(default=list)
    uploaded_at       = models.DateTimeField(auto_now_add=True)
    expires_at        = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"PortalSession {self.session_key}"
