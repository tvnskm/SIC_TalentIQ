from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from common.validators import ResumeValidator
from common.exceptions import InvalidFileFormatError, FileSizeTooLargeError
from django.contrib import messages
from .models import PortalSession
from .services import PortalResumeService

class CandidatePortalHome(View):
    template_name = 'candidate/index.html'

    def get(self, request):
        from jobs.models import Job
        return render(request, self.template_name, {
            'featured_jobs': Job.objects.order_by('-created_at')[:6],
        })


class PortalUploadView(View):
    def post(self, request):
        uploaded_file = request.FILES.get('resume_file')
        if not uploaded_file:
            messages.error(request, 'Please select a resume file.')
            return redirect('portal:home')
        try:
            ResumeValidator().validate(uploaded_file)
        except (InvalidFileFormatError, FileSizeTooLargeError) as e:
            messages.error(request, str(e))
            return redirect('portal:home')

        session = PortalResumeService().process_upload(uploaded_file)
        return redirect('portal:results', key=session.session_key)


class PortalResultsView(View):
    template_name = 'candidate/results.html'

    def get(self, request, key):
        session = get_object_or_404(PortalSession, session_key=key)
        if session.is_expired():
            messages.error(request, 'Session expired. Please upload again.')
            return redirect('portal:home')
        return render(request, self.template_name, {
            'session':   session,
            'top_match': session.job_matches[0] if session.job_matches else None,
        })


class PortalGapView(View):
    template_name = 'candidate/skill_gap.html'

    def get(self, request, key, job_pk):
        from jobs.models import Job
        session = get_object_or_404(PortalSession, session_key=key)
        job     = get_object_or_404(Job, pk=job_pk)

        # Find this job's data from session
        job_data = next(
            (m for m in session.job_matches if m['job_id'] == job_pk),
            None
        )
        return render(request, self.template_name, {
            'session':  session,
            'job':      job,
            'job_data': job_data,
        })


class PortalImproveView(View):
    template_name = 'candidate/improve.html'

    def get(self, request, key):
        session     = get_object_or_404(PortalSession, session_key=key)
        suggestions = PortalResumeService().get_improvement_suggestions(session)
        return render(request, self.template_name, {
            'session':     session,
            'suggestions': suggestions,
        })


class PortalReportDownloadView(View):
    """Generates an HTML report and returns it as a downloadable file.
    Nothing is stored — generated on-the-fly from PortalSession."""

    def get(self, request, key):
        from django.template.loader import render_to_string
        session = get_object_or_404(PortalSession, session_key=key)
        html    = render_to_string('candidate/report.html', {'session': session})
        response = HttpResponse(html, content_type='text/html')
        response['Content-Disposition'] = \
            f'attachment; filename="resume_report_{key}.html"'
        return response
