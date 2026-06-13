from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from jobs.models import Job
import json

class SimulatorView(View):
    template_name = 'hr/simulator/index.html'

    def get(self, request):
        jobs = Job.objects.prefetch_related('jobskill_set__skill').all()
        return render(request, self.template_name, {'jobs': jobs})


class SimulatorRecalculateView(View):
    """AJAX endpoint — returns re-ranked JSON without touching DB."""

    def post(self, request):
        from .services import SimulatorService
        try:
            body         = json.loads(request.body)
            job_id       = int(body.get('job_id'))
            custom_w     = body.get('skill_weights', {})  # {skill_name: weight}
            exp_w        = float(body.get('exp_weight', 0.20))
            cert_w       = float(body.get('cert_weight', 0.10))
            ranked       = SimulatorService().simulate(
                               job_id, custom_w, exp_w, cert_w)
            return JsonResponse({'status': 'ok', 'rankings': ranked})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
