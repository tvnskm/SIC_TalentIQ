import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talentiq.settings')
django.setup()

from django.test import Client

client = Client()

urls_to_test = [
    '/hr/jobs/upload/',
    '/hr/candidates/bulk-upload/',
]

for url in urls_to_test:
    try:
        response = client.get(url)
        print(f'{url}: {response.status_code}')
    except Exception as e:
        print(f'{url}: ERROR - {e}')
