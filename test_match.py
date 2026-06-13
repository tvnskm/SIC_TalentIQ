import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talentiq.settings')
django.setup()

from django.test import Client
from jobs.models import Job

job = Job.objects.first()
if not job:
    job = Job.objects.create(title="Software Engineer", min_experience=2.0)

client = Client()
try:
    response = client.get(f'/hr/matching/{job.pk}/run/')
    print(f'Match Run Status: {response.status_code}')
except Exception as e:
    import traceback
    traceback.print_exc()
