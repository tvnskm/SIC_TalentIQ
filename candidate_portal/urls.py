from django.urls import path
from .views import (
    CandidatePortalHome, PortalUploadView, PortalResultsView,
    PortalGapView, PortalImproveView,
    PortalReportDownloadView
)

app_name = 'portal'

urlpatterns = [
    path('',                            CandidatePortalHome.as_view(),
                                        name='home'),
    path('upload/',                     PortalUploadView.as_view(),
                                        name='upload'),
    path('results/<uuid:key>/',         PortalResultsView.as_view(),
                                        name='results'),
    # Temporary views for missing portal endpoints
    path('recommendations/<uuid:key>/', PortalResultsView.as_view(),
                                        name='recommendations'),
    path('gap/<uuid:key>/<int:job_pk>/',PortalGapView.as_view(),
                                        name='gap'),
    path('improve/<uuid:key>/',         PortalImproveView.as_view(),
                                        name='improve'),
    path('report/<uuid:key>/download/', PortalReportDownloadView.as_view(),
                                        name='report'),
]
