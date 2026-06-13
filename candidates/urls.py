from django.urls import path
from .views import DashboardView, CandidateListView, CandidateDetailView, CandidateBulkUploadView, CandidateExportCSVView, CandidateUpdateView, CandidateDeleteView
from matching.views import CandidateCompareView

app_name = 'candidates'
urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('candidates/', CandidateListView.as_view(), name='list'),
    path('candidates/export/', CandidateExportCSVView.as_view(), name='export'),
    path('candidates/bulk-upload/', CandidateBulkUploadView.as_view(), name='bulk_upload'),
    path('candidates/<int:pk>/', CandidateDetailView.as_view(), name='detail'),
    path('candidates/<int:pk>/edit/', CandidateUpdateView.as_view(), name='edit'),
    path('candidates/<int:pk>/delete/', CandidateDeleteView.as_view(), name='delete'),
    path('candidates/compare/', CandidateCompareView.as_view(), name='compare'),
]
