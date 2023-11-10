from django.http import HttpResponse
from django.db.models import Count, Q
from django.shortcuts import render
from .models import Recruiter, MessageThread
from .score_calc import ScoreCalc

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528


def inbox(request):
    recruiter = Recruiter.objects.get(id=RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter=recruiter).select_related('candidate', 'job')
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
        'candidate': thread.candidate,
    }
    return render(request, 'inbox/thread.html', _context)


def sort_by_score(request):
    recruiter = Recruiter.objects.get(id=RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter=recruiter).select_related('candidate', 'job')
    jobs_ = dict()
    for thread in threads:
        candidate = thread.candidate
        job = thread.job
        candidate_score = ScoreCalc(candidate, job).get_score()
        if job in jobs_:
            jobs_[job].append((candidate_score, thread))
        else:
            jobs_[job] = [(candidate_score, thread), ]
    for job, scored_items in jobs_.items():
        scored_items.sort(key=lambda x: x[0], reverse=True)
    _context = {'title': "Djinni - Inbox", 'recruiter': recruiter, 'jobs': jobs_}
    return render(request, 'inbox/sort_by_score.html', _context)
