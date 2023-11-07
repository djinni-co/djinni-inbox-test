from django.shortcuts import render

from .analyzator import Analyzator

from .models import Recruiter, MessageThread
from django.db.models.query import QuerySet

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528
analyzator = Analyzator()


def inbox(request):
    recruiter = Recruiter.objects.get(id = RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter = recruiter).select_related('candidate', 'job')

    threads = sorted(threads, key=lambda x: analyzator.calc_priority(x), reverse=False)

    _context = { 'title': "Djinni - Inbox", 'recruiter': recruiter, 'threads': threads }

    return render(request, 'inbox/chats.html', _context)

def inbox_thread(request, pk):
    thread = MessageThread.objects.get(id = pk)
    messages = thread.message_set.all().order_by('created')

    distance = analyzator.get_candidate_job_distance(thread)

    _context = {
        'pk': pk,
        'title': "Djinni - Inbox",
        'thread': thread,
        'messages': messages,
        'candidate': thread.candidate,
        'distance': distance,
    }

    return render(request, 'inbox/thread.html', _context)
