import json
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from matching.services import MatchingService, SkillGapService
from matching.models import CandidateJobMatch, SkillGapAnalysis
from jobs.models import Job
from candidates.models import Candidate

class RunMatchingView(View):
    """Endpoint to trigger the matching engine for a job."""

    def get(self, request, job_pk):
        from django.contrib import messages
        try:
            MatchingService().run_matching_for_job(job_pk)
            messages.success(request, 'Matching completed successfully.')
            return redirect('matching:results', job_pk=job_pk)
        except Exception as e:
            messages.error(request, f'Error running match: {e}')
            return redirect('jobs:list')

    def post(self, request, job_pk):
        try:
            result = MatchingService().run_matching_for_job(job_pk)
            return JsonResponse({'status': 'success', **result})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class MatchingResultsView(View):
    template_name = 'hr/matching/results.html'

    def get(self, request, job_pk):
        job = get_object_or_404(Job, pk=job_pk)
        matches = (CandidateJobMatch.objects
                   .filter(job=job)
                   .select_related('candidate')
                   .order_by('rank'))

        return render(request, self.template_name, {
            'job':     job,
            'matches': matches,
            'total':   matches.count(),
        })


class ExplainMatchView(View):
    """Explainable AI — shows score breakdown with visual bars."""
    template_name = 'hr/matching/explain.html'

    def get(self, request, job_pk, candidate_pk):
        match = get_object_or_404(
            CandidateJobMatch,
            job_id=job_pk,
            candidate_id=candidate_pk
        )
        job       = match.job
        candidate = match.candidate

        # Skill details: which skills matched, which didn't
        job_skill_names  = set(js.skill.skill_name.lower()
                                for js in job.jobskill_set.select_related('skill').all())
        cand_skill_names = set(cs.skill.skill_name.lower()
                                for cs in candidate.candidateskill_set
                                             .select_related('skill').all())

        matched_skills = job_skill_names & cand_skill_names
        missing_skills = job_skill_names - cand_skill_names

        # Weight breakdown per skill
        skill_breakdown = []
        for js in job.jobskill_set.select_related('skill').all():
            name = js.skill.skill_name.lower()
            skill_breakdown.append({
                'skill':    js.skill.skill_name,
                'weight':   js.weight,
                'matched':  name in cand_skill_names,
            })

        return render(request, self.template_name, {
            'match':           match,
            'job':             job,
            'candidate':       candidate,
            'matched_skills':  matched_skills,
            'missing_skills':  missing_skills,
            'skill_breakdown': skill_breakdown,
            # Score component bars (for CSS width)
            'skill_bar':       min(match.skill_score, 100),
            'exp_bar':         min(match.experience_score, 100),
            'cert_bar':        min(match.certification_score, 100),
            'total_bar':       min(match.match_percentage, 100),
        })


class SkillGapView(View):
    template_name = 'hr/matching/skill_gap.html'

    def get(self, request, job_pk, candidate_pk):
        gap = get_object_or_404(
            SkillGapAnalysis,
            job_id=job_pk,
            candidate_id=candidate_pk
        )
        return render(request, self.template_name, {
            'gap':       gap,
            'job':       gap.job,
            'candidate': gap.candidate,
        })


class CandidateCompareView(View):
    template_name = 'hr/matching/compare.html'

    def get(self, request):
        ids = request.GET.get('ids', '')
        candidate_ids = [int(i) for i in ids.split(',') if i.isdigit()]
        candidates = Candidate.objects.filter(pk__in=candidate_ids) \
                                      .prefetch_related('candidateskill_set__skill')

        job_id = request.GET.get('job_id')
        matches = {}
        if job_id:
            for m in CandidateJobMatch.objects.filter(
                    candidate_id__in=candidate_ids, job_id=job_id):
                matches[m.candidate_id] = m

        return render(request, self.template_name, {
            'candidates': candidates,
            'matches':    matches,
            'job_id':     job_id,
            'all_jobs':   Job.objects.all(),
        })
