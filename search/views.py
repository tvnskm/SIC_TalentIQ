from django.views import View
from django.shortcuts import render
from .services import SearchService
from candidates.models import Candidate

class SearchView(View):
    template_name = 'hr/search/index.html'

    def get(self, request):
        svc    = SearchService()
        params = request.GET

        skill       = params.get('skill')
        min_exp     = params.get('min_exp')
        max_exp     = params.get('max_exp')
        education   = params.get('education')
        cert        = params.get('certification')

        results_ids = None
        algo_used = []

        if skill:
            ids = set(c.id for c in svc.search_by_skill(skill))
            results_ids = ids if results_ids is None else results_ids.intersection(ids)
            algo_used.append('Hash Table (Skill)')
            
        if min_exp or max_exp:
            ids = set(c.id for c in svc.search_by_experience(float(min_exp or 0), float(max_exp or 99)))
            results_ids = ids if results_ids is None else results_ids.intersection(ids)
            algo_used.append('Binary Search (Exp)')
            
        if education:
            ids = set(c.id for c in svc.search_by_education(education))
            results_ids = ids if results_ids is None else results_ids.intersection(ids)
            algo_used.append('DB Query (Edu)')
            
        if cert:
            ids = set(c.id for c in svc.search_by_certification(cert))
            results_ids = ids if results_ids is None else results_ids.intersection(ids)
            algo_used.append('DB Query (Cert)')

        final_results = None
        algo_str = None
        if results_ids is not None:
            final_results = Candidate.objects.filter(id__in=results_ids)
            algo_str = ' + '.join(algo_used)

        return render(request, self.template_name, {
            'results':   final_results,
            'algo_used': algo_str,
            'params':    params,
        })
