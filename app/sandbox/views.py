from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.db.models import Count, Q, Avg, F, Max, Min, Window
from django.shortcuts import render, reverse, get_object_or_404

from . import constants as C

from .models import Recruiter, MessageThread, JobPosting, EnglishLevel

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

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

        # TODO: Skills measuring is NIY
        thr.scores['skills'] = 0

        thr.scores['total'] = (
              thr.scores['experience'] * weights['experience']
            + thr.scores['skills']     * weights['skills']
            + thr.scores['english']    * weights['english']

            # the higher the salary the higher should be the penalty
            - thr.scores['salary']     * weights['salary']
        )

    # from the highest score to the lowest
    return sorted(thrs_ext, key = lambda v: v.scores['total'],
                     reverse = True)

def inbox(req):
    context = { 'const': C.inbox, 'min': min, 'int': int }

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
    threads = MessageThread.objects.filter( recruiter = recruiter )

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
        # FIXME: filter out Jobs that are not referenced by any MessageThread
        'jobs': JobPosting.objects.filter(
            recruiter = recruiter,
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
