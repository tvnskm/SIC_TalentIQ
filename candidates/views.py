from django.views.generic import ListView, DetailView, TemplateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .models import Candidate, CandidateSkill, Certification
from matching.models import CandidateJobMatch, SkillGapAnalysis
from jobs.models import Job
from analytics.services import AnalyticsService
from analytics.chart_service import ChartService

class DashboardView(TemplateView):
    template_name = 'hr/dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        svc    = AnalyticsService()
        charts = ChartService()

        summary = svc.get_dashboard_summary()
        ctx.update({
            # ── Stat cards ──
            'total_candidates':    summary['total_candidates'],
            'total_jobs':          summary['total_jobs'],
            'avg_match_score':     summary['average_match_score'],
            'top_candidate':       summary['top_ranked_candidate'],

            # ── Tables ──
            'top_ranked':          svc.get_top_ranked_candidates(top_n=10),
            'recent_jobs':         Job.objects.order_by('-created_at')[:5],

            # ── Mini charts (base64 PNG) ──
            'chart_top_skills':    charts.top_skills_chart(svc.get_top_skills(5)),
            'chart_exp_dist':      charts.experience_distribution_chart(
                                       svc.get_experience_statistics()),
        })
        return ctx

class CandidateListView(ListView):
    model = Candidate
    template_name = 'hr/candidates/list.html'
    context_object_name = 'candidates'
    paginate_by = 10

    def get_queryset(self):
        qs = Candidate.objects.prefetch_related(
            'candidateskill_set__skill'
        ).order_by('-created_at')

        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q) | \
                 qs.filter(email__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_count'] = Candidate.objects.count()
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx


class CandidateDetailView(DetailView):
    model = Candidate
    template_name = 'hr/candidates/detail.html'
    context_object_name = 'candidate'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        candidate = self.object
        ctx['skills']      = CandidateSkill.objects.filter(
                                candidate=candidate).select_related('skill')
        ctx['certs']       = Certification.objects.filter(candidate=candidate)
        ctx['matches']     = CandidateJobMatch.objects.filter(
                                candidate=candidate).select_related('job') \
                                .order_by('-match_percentage')
        ctx['skill_gaps']  = SkillGapAnalysis.objects.filter(
                                candidate=candidate).select_related('job')
        return ctx

import csv
import io
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

class CandidateBulkUploadView(View):
    template_name = 'hr/candidates/bulk_upload.html'
    
    def get(self, request):
        return render(request, self.template_name)
        
    def post(self, request):
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return render(request, self.template_name)
            
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a CSV.')
            return render(request, self.template_name)
            
        try:
            # Read CSV
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            # Skip header
            next(io_string, None)
            
            from candidates.models import Candidate, Skill, CandidateSkill, Certification
            
            count = 0
            for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                if len(row) < 6:
                    continue
                name, email, phone, education, exp, skills_str = row[:6]
                certs_str = row[6] if len(row) >= 7 else ""
                
                # Check if exists
                if Candidate.objects.filter(email=email).exists():
                    continue
                    
                try:
                    exp = float(exp)
                except ValueError:
                    exp = 0.0
                    
                cand = Candidate.objects.create(
                    name=name.strip(),
                    email=email.strip(),
                    phone=phone.strip(),
                    education=education.strip(),
                    experience_years=exp,
                    resume_score=80.0
                )
                
                # Attach skills
                for s_name in skills_str.split(','):
                    s_name = s_name.strip()
                    if s_name:
                        skill_obj, _ = Skill.objects.get_or_create(skill_name=s_name, defaults={'category': 'Bulk Imported'})
                        CandidateSkill.objects.create(candidate=cand, skill=skill_obj, proficiency_level='Intermediate')
                
                # Attach certifications
                for c_name in certs_str.split(','):
                    c_name = c_name.strip()
                    if c_name:
                        Certification.objects.create(candidate=cand, certificate_name=c_name, issuer='Unknown')
                
                count += 1
                
            messages.success(request, f'Successfully imported {count} candidates.')
            return redirect('candidates:list')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return render(request, self.template_name)

from django.http import HttpResponse

class CandidateExportCSVView(View):
    def get(self, request):
        from reports.services import ReportService
        csv_data = ReportService().export_candidates_csv()
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="all_candidates.csv"'
        return response

class CandidateUpdateView(UpdateView):
    model = Candidate
    template_name = 'hr/candidates/form.html'
    fields = ['name', 'email', 'phone', 'education', 'experience_years']
    
    def get_success_url(self):
        messages.success(self.request, 'Candidate updated successfully.')
        return reverse_lazy('candidates:detail', kwargs={'pk': self.object.pk})

class CandidateDeleteView(DeleteView):
    model = Candidate
    template_name = 'hr/candidates/confirm_delete.html'
    success_url = reverse_lazy('candidates:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Candidate deleted successfully.')
        return super().delete(request, *args, **kwargs)
