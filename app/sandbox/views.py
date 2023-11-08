from typing import Final

from django.shortcuts import render

from .models import Recruiter, MessageThread
from .scorer import SimilarityInboxScorer

RECRUITER_ID: Final[int] = 125528
THREADS_LIMIT: Final[int] = 10


def inbox(request):
    recruiter = Recruiter.objects.get(id=RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter=recruiter).select_related('candidate', 'job')[:THREADS_LIMIT]

    scorer = SimilarityInboxScorer(threads)

    _context = {'title': "Djinni - Inbox", 'recruiter': recruiter, 'threads': threads, 'scores': scorer.score()}

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
