import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talentiq.settings')
django.setup()

from django.test import Client
from django.urls import reverse

client = Client()

urls_to_test = [
    '/hr/dashboard/',
    '/hr/candidates/',
    '/hr/resumes/upload/',
    '/hr/jobs/',
    '/hr/jobs/add/',
    '/hr/search/',
    '/hr/analytics/',
    '/hr/simulator/',
    '/candidate/',
    '/candidate/upload/'
]

for url in urls_to_test:
    try:
        response = client.get(url)
        print(f'{url}: {response.status_code}')
    except Exception as e:
        print(f'{url}: ERROR - {e}')
