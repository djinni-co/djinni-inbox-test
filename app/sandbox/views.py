from django.http import HttpResponse
from django.db.models import Count, Q
from django.shortcuts import render

from .models import Recruiter, MessageThread
from .scoring import score_thread

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528


def inbox(request):
    sort = request.GET.get('sort')
    recruiter = Recruiter.objects.get(id=RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter=recruiter).select_related('candidate', 'job')

    if sort == 'score':
        threads = sorted({score_thread(thread) for thread in threads}, key=lambda thread: thread.score, reverse=True)

    _context = {'title': "Djinni - Inbox", 'recruiter': recruiter, 'threads': threads}

    return render(request, 'inbox/chats.html', _context)


def inbox_thread(request, pk):
    thread = MessageThread.objects.get(id=pk)
    messages = thread.message_set.all().order_by('created')

    _context = {
        'pk': pk,
        'title': "Djinni - Inbox",
        'thread': thread,
        'messages': messages,
        'candidate': thread.candidate
    }

    return render(request, 'inbox/thread.html', _context)
