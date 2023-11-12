from django.http import HttpResponse
from django.db.models import Count, Q
from django.shortcuts import render


from .models import Recruiter, MessageThread
from .utils.match_score_calculator import MatchScoreCalculator

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

def inbox(request):
    recruiter = Recruiter.objects.get(id = RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter = recruiter).select_related('candidate', 'job')

    # TODO: precalculate && move to DB
    match_metrics = {}
    match_metrics_score = {}
    for thread in threads:
        calculator = MatchScoreCalculator(thread.candidate, thread.job)
        metrics = calculator.get_metrics()
        match_metrics[thread.id] = metrics
        match_metrics_score[thread.id] = sum(metrics.values())

    sorted_threads = sorted(threads, key=lambda x: match_metrics_score[x.id], reverse=True)

    _context = {
        'title': "Djinni - Inbox",
        'recruiter': recruiter,
        'threads': sorted_threads,
        'match_metrics': match_metrics,
        'match_metrics_score': match_metrics_score,
    }

    return render(request, 'inbox/chats.html', _context)

def inbox_thread(request, pk):
    thread = MessageThread.objects.get(id = pk)
    messages = thread.message_set.all().order_by('created')

    _context = {
        'pk': pk,
        'title': "Djinni - Inbox",
        'thread': thread,
        'messages': messages,
        'candidate': thread.candidate,
    }

    return render(request, 'inbox/thread.html', _context)
