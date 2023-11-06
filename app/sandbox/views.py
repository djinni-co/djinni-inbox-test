from django.shortcuts import render
from django.utils import timezone

from .models import Recruiter, MessageThread, JobPosting, Message
from django.db.models import F, ExpressionWrapper, DateTimeField, Subquery, OuterRef
from django.db.models.functions import Abs
from .utils import Epoch
from django.views.decorators.cache import cache_page

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528


def inbox(request):
    recruiter = Recruiter.objects.get(id=RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter=recruiter).select_related('candidate', 'job')

    _context = {'title': "Djinni - Inbox", 'recruiter': recruiter, 'threads': threads}

    return render(request, 'inbox/chats.html', _context)


# @cache_page(60)
def job_postings(request):
    current_time = timezone.now()

    subquery = Message.objects.filter(
        job=OuterRef('pk'),
        recruiter=RECRUITER_ID
    ).annotate(
        closest_created_at=Abs(Epoch(ExpressionWrapper(
                    current_time - F('created'),
                    output_field=DateTimeField()
                )))

    ).order_by('closest_created_at')

    job_postings_qs = JobPosting.objects.filter(recruiter=RECRUITER_ID).annotate(
        closest_message=Subquery(subquery.values('closest_created_at')[:1])
    ).order_by('closest_message')

    _context = {'title': "Djinni - Inbox", 'job_postings': job_postings_qs}
    return render(request, 'jobs/job_postings.html', _context)

# @cache_page(60)
def job_post_threads(request, pk):
    query_param = request.GET.get('q')
    job = JobPosting.objects.get(id=pk)
    show_score = False
    if query_param == 'best_match':
        show_score = True
        threads = MessageThread.objects.get_ordered_by_best_match(job=job)
    else:
        threads = MessageThread.objects.get_ordered_by_newest_message(job=job)
    _context = {'title': "Djinni - Inbox", 'threads': threads, "show_score": show_score, "job_post_id": pk}
    return render(request, 'inbox/chats.html', _context)


def inbox_thread(request, pk):
    thread = MessageThread.objects.get(id=pk)
    messages = thread.message_set.all().order_by('created')

    _context = {
        'pk': pk,
        'title': "Djinni - Inbox",
        'thread': thread,
        'messages': messages,
        'candidate': thread.candidate,
    }

    return render(request, 'inbox/thread.html', _context)
