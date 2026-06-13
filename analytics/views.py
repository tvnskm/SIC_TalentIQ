from django.views.generic import TemplateView
from .services import AnalyticsService
from .chart_service import ChartService

class AnalyticsDashboardView(TemplateView):
    template_name = 'hr/analytics/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        svc    = AnalyticsService()
        charts = ChartService()

        top_skills = svc.get_top_skills(10)
        exp_stats  = svc.get_experience_statistics()
        edu_dist   = svc.get_education_distribution()
        match_dist = svc.get_match_score_distribution()
        cert_dist  = svc.get_certification_distribution()

        ctx.update({
            # Summary cards
            **svc.get_dashboard_summary(),

            # Chart images (base64)
            'chart_skills':   charts.top_skills_chart(top_skills),
            'chart_exp':      charts.experience_distribution_chart(exp_stats),
            'chart_edu':      charts.education_distribution_chart(edu_dist),
            'chart_match':    charts.match_score_histogram(match_dist),
            'chart_cert':     charts.certification_distribution_chart(cert_dist),

            # Table data
            'top_skills':     top_skills,
            'exp_stats':      exp_stats,
            'top_candidates': svc.get_top_ranked_candidates(top_n=10),
        })
        return ctx

class JobAnalyticsView(TemplateView):
    template_name = 'hr/analytics/job_dashboard.html'
    
    def get_context_data(self, **kwargs):
        import json
        from jobs.models import Job
        from django.shortcuts import get_object_or_404
        
        ctx = super().get_context_data(**kwargs)
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(Job, pk=job_id)
        
        svc = AnalyticsService()
        charts = ChartService()
        data = svc.get_job_specific_analytics(job_id)
        
        ctx.update({
            'job': job,
            'chart_skills': charts.generic_bar_chart('Top Skills Demanded vs Available', data['top_skills'], 'Number of Candidates', 'Skill'),
            'chart_match': charts.generic_pie_chart('Match Score Distribution', data['match_distribution']),
            'chart_exp': charts.generic_pie_chart('Applicant Experience Levels', data['experience_distribution']),
        })
        return ctx
