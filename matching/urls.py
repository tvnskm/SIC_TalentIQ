from django.urls import path
from .views import RunMatchingView, MatchingResultsView, ExplainMatchView, SkillGapView

app_name = 'matching'
urlpatterns = [
    path('matching/<int:job_pk>/run/', RunMatchingView.as_view(), name='run'),
    path('matching/<int:job_pk>/results/', MatchingResultsView.as_view(), name='results'),
    path('matching/<int:job_pk>/explain/<int:candidate_pk>/', ExplainMatchView.as_view(), name='explain'),
    path('matching/<int:job_pk>/gap/<int:candidate_pk>/', SkillGapView.as_view(), name='skill_gap'),
    # select job view is actually just the job list or dashboard for now
]
