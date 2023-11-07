from django.http import HttpResponse
from django.db.models import Count, Q
from django.shortcuts import render

from .models import Recruiter, MessageThread, JobPosting, Candidate

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


def jobs(request):
    jobPosting = JobPosting.objects.all()
    _context = {'title': "Djinni - Jobs", 'jobPosting': jobPosting}

    return render(request, 'jobs/job_list.html', _context)


def jobs_candidates(request, pk):
    job = JobPosting.objects.get(id=pk)
    candidates = Candidate.objects.all()
    english_levels = ['basic', 'pre', 'intermediate', 'upper', 'fluent']

    for candidate in candidates:
        candidate.score = candidate.experience_years
        candidate.score += english_levels.index(candidate.english_level)
        if job.primary_keyword == candidate.primary_keyword:
            candidate.score += 5


    _context = {'title': "Djinni - Candidates", 'job': job, 'candidates': sorted(candidates, key=lambda x: x.score, reverse=True)}

    return render(request, 'jobs/job_perfect_candidates.html', _context)
