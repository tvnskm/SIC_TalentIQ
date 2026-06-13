from django.urls import path
from .views import ResumeUploadView, ResumePreviewView, ResumeConfirmView, ResumeBulkUploadView

app_name = 'resumes'
urlpatterns = [
    path('resumes/upload/', ResumeUploadView.as_view(), name='upload'),
    path('resumes/bulk-upload/', ResumeBulkUploadView.as_view(), name='bulk_upload'),
    path('resumes/<int:pk>/preview/', ResumePreviewView.as_view(), name='preview'),
    path('resumes/<int:pk>/confirm/', ResumeConfirmView.as_view(), name='confirm'),
]
