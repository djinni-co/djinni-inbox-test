from typing import Final

from django.shortcuts import render

from .enums import ThreadsSort
from .models import Recruiter, MessageThread
from .scorer import SimilarityInboxScorer

RECRUITER_ID: Final[int] = 125528

THREADS_LIMIT: Final[int] = 70
THREADS_SORT_PARAM: Final[str] = 'sort'
PAGE_TITLE: Final[str] = 'Djinni - Inbox'


def inbox(request):
    sort = request.GET.get(THREADS_SORT_PARAM, ThreadsSort.RECENT)

    recruiter = Recruiter.objects.get(id=RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter=recruiter).select_related('candidate', 'job')[:THREADS_LIMIT]

    scorer = SimilarityInboxScorer(threads)
    scored_threads = zip(threads, scorer.score())

    _context = {
        'title': PAGE_TITLE,
        'recruiter': recruiter,
        'sort': f'Most {sort}',
        'scored_threads': scored_threads if sort == ThreadsSort.RECENT
        else sorted(scored_threads, key=lambda x: x[1], reverse=True)
    }

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
