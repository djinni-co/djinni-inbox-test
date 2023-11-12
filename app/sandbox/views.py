import re

from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.db.models import Count, Q, Avg, F, Max, Min, Window
from django.shortcuts import render, reverse, get_object_or_404

from . import constants as C

from .models import Recruiter, MessageThread, JobPosting, EnglishLevel

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

GENERIC_SKILLS = [
    'english',
    'responsibility',
    'responsible',
    'make',
    'architecture',
    'website',
    'communication',
    'next',
    'web',
    'system',
]

def _calc_tech_similarity (candidate, job):
    sim = 0
    if candidate.primary_keyword == job.primary_keyword:
        sim += 0.9

    if candidate.secondary_keyword == job.primary_keyword:
        sim += 0.5

    if candidate.primary_keyword == job.secondary_keyword:
        sim += 0.25

    if candidate.secondary_keyword == job.secondary_keyword:
        sim += 0.1

    return min(sim, 1)

def _extract_skills_from_job_desc (job, all_skills):
    batch_search = '%s' % '|'.join([ re.escape(s) for s in all_skills ])

    matches = set(re.findall(
        r'\b(%s)\b' % batch_search,
        job.long_description.casefold()
    ))

    position_dups = set([ sk for sk in matches if sk in job.position ])

    return matches - set([
        # remove duplicates of primary & secondary keywords
        (job.primary_keyword or '').casefold(),
        (job.secondary_keyword or '').casefold(),
        *GENERIC_SKILLS,
    ]) - position_dups

def _find_skills_match (job, candidate):
    cand_skills = candidate.skills_cache_list()
    return set(job.extracted_skills).intersection(set(cand_skills))

def _find_all_unique_candidate_skills (candidates_or_threads):
    all_skills = set()

    candidates = candidates_or_threads
    if getattr(candidates_or_threads[0], 'candidate', None):
        candidates = set([ thr.candidate for thr in candidates_or_threads ])

    for c in candidates:
        all_skills.update( c.skills_cache_list() )

    return all_skills

def _apply_advanced_sorting (threads, weights):
    window = {
       'partition_by': [F('job_id')],
    }

    thrs_ext = threads.annotate(
        cand_min_sal = Window(
            expression = Min('candidate__salary_min'), **window,
        ),

        cand_max_sal = Window(
            expression = Max('candidate__salary_min'), **window,
        ),

        cand_min_exp = Window(
            expression = Min('candidate__experience_years'), **window,
        ),

        cand_max_exp = Window(
            expression = Max('candidate__experience_years'), **window,
        ),
    )

    all_skills = _find_all_unique_candidate_skills(thrs_ext)

    # FIXME: this value must be computed based on priority of skills for the
    # Job which itself must be extracted from the Job somehow (hint:
    # presumably recruiter specifies more important things top-to-bottom
    # left-to-right)
    best_skillset = 0

    for thr in thrs_ext:
        thr.scores = {}

        exp_range = thr.cand_max_exp - thr.cand_min_exp
        thr.scores['experience'] = (
            thr.candidate.experience_years - thr.cand_min_exp
        ) / exp_range

        sal_range = thr.cand_max_sal - thr.cand_min_sal
        thr.scores['salary'] = (
            thr.candidate.salary_min - thr.cand_min_sal
        ) / sal_range

        # Divide by 5 since there are levels from 0 to 5 (including)
        thr.scores['english'] = int(
            EnglishLevel(thr.candidate.english_level)
        ) / 5

        # TODO: this list should be cached into the DB (don't forget to
        # invalidate the cache properly!)
        if not getattr(thr.job, 'extracted_skills', None):
            thr.job.extracted_skills = _extract_skills_from_job_desc(
                thr.job, all_skills)

        # skills match must be computed in this loop but analyzed in the next
        thr.matching_skills = _find_skills_match(thr.job, thr.candidate)
        best_skillset = max(best_skillset, len(thr.matching_skills))

        thr.scores['tech_sim'] = _calc_tech_similarity(thr.candidate, thr.job)

    # since the number of skills is varying, their analysis must be done after
    # all of the info (how many skills of each Candidate matches with the Job)
    # is available
    for thr in thrs_ext:
        thr.scores['skills'] = len(thr.matching_skills) / best_skillset
        # thr.scores['skills'] = len(thr.matching_skills) / len(thr.job.extracted_skills)

        thr.scores['total'] = (
              thr.scores['experience'] * weights['experience'] * thr.scores['tech_sim']
            + thr.scores['skills']     * weights['skills']
            + thr.scores['english']    * weights['english']

            # the higher the salary the higher should be the penalty
            - thr.scores['salary']     * weights['salary']
        )

    # from the highest score to the lowest
    return sorted(thrs_ext, key = lambda v: v.scores['total'],
                  reverse = True)

def inbox(req):
    context = { 'const': C.inbox, 'max': max, 'int': int }

    get_params = QueryDict('', mutable=True)
    get_params.update(req.GET)

    page = int(req.GET.get(C.inbox.http.param.PAGING) or 1)
    sorting = req.GET.get( C.inbox.http.param.SORTING )
    sorting = C.inbox.sorting.str2obj(sorting) or C.inbox.sorting.DEFAULT

    current_job = None
    job_filter = int( req.GET.get( C.inbox.http.param.JOB_FILTER ) or -1)
    if job_filter != -1:
        current_job = get_object_or_404(JobPosting, pk = job_filter)
        context |= { 'current_job': current_job }

    recruiter = Recruiter.objects.get(id = RECRUITER_ID)
    all_thrs = threads = MessageThread.objects.filter( recruiter = recruiter )

    if current_job:
        threads = threads.filter( job__id = job_filter )

    threads = threads.select_related('candidate', 'job')

    if sorting is C.inbox.sorting.recent:
        pass
    elif sorting is C.inbox.sorting.advanced:
        # The main deal
        wt_salary     = get_params.get(C.inbox.http.param.ast.SALARY)
        wt_experience = get_params.get(C.inbox.http.param.ast.EXPERIENCE)
        wt_skills     = get_params.get(C.inbox.http.param.ast.SKILLS)
        wt_english    = get_params.get(C.inbox.http.param.ast.ENGLISH)

        if None not in [wt_salary, wt_experience, wt_skills]:
            context |= {
                'ast_salary': wt_salary,
                'ast_experience': wt_experience,
                'ast_skills': wt_skills,
                'ast_english': wt_english,
            }

            wt_salary     = int(wt_salary) / 100
            wt_experience = int(wt_experience) / 100
            wt_skills     = int(wt_skills) / 100
            wt_english    = int(wt_english) / 100

            if None not in [wt_salary, wt_experience, wt_skills]:
                threads = _apply_advanced_sorting(threads, {
                    'salary': wt_salary,
                    'experience': wt_experience,
                    'skills': wt_skills,
                    'english': wt_english,
                })
    else:
        raise ValueError('Sorting algorithm is incorrect!')

    threads = threads[
          (page - 1) * C.inbox.paging.PER_PAGE
        : page * C.inbox.paging.PER_PAGE
    ]

    context |= {
        'sorting_options': C.inbox.sorting.AVAILABLE_METHODS,
        'current_sorting': sorting,
    }

    get_params[C.inbox.http.param.PAGING] = page + 1
    context |= {
        'next_page_url': '%s?%s' % (
            reverse('sb:inbox'),
            get_params.urlencode(),
        ),
    }

    context |= {
        'jobs': JobPosting.objects.filter(
            recruiter = recruiter,
            id__in = set([ t.job_id for t in all_thrs ]),
        ).all()
    }

    context |= {
        'title': "Djinni - Inbox",
        'recruiter': recruiter,
        'threads': threads,
    }

    template = 'inbox/chats.html'
    if req.headers.get('Hx-Request') == 'true':
        template = 'inbox/mixin/chat-list.jinja'

    return render(req, template, context)

def inbox_thread(req, pk):
    thread = MessageThread.objects.get(id = pk)
    messages = thread.message_set.all().order_by('created')

    context = {
        'pk': pk,
        'title': "Djinni - Inbox",
        'thread': thread,
        'messages': messages,
        'candidate': thread.candidate,
    }

    return render(req, 'inbox/thread.html', context)
