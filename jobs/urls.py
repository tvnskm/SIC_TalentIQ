from django.urls import path
from .views import JobListView, JobDetailView, JobCreateView, JobUploadView, JobUploadConfirmView, JobAssignCandidatesView, JobBulkUploadCandidatesView

app_name = 'jobs'
urlpatterns = [
    path('jobs/', JobListView.as_view(), name='list'),
    path('jobs/add/', JobCreateView.as_view(), name='add'),
    path('jobs/upload/', JobUploadView.as_view(), name='upload'),
    path('jobs/upload/confirm/', JobUploadConfirmView.as_view(), name='upload_confirm'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='detail'),
    path('jobs/<int:pk>/assign/', JobAssignCandidatesView.as_view(), name='assign'),
    path('jobs/<int:pk>/bulk-upload/', JobBulkUploadCandidatesView.as_view(), name='bulk_upload'),
]
