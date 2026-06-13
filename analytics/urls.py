from django.urls import path
from .views import AnalyticsDashboardView, JobAnalyticsView

app_name = 'analytics'
urlpatterns = [
    path('analytics/', AnalyticsDashboardView.as_view(), name='dashboard'),
    path('analytics/job/<int:job_id>/', JobAnalyticsView.as_view(), name='job_dashboard'),
]
