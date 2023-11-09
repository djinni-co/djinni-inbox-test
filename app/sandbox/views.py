from django.http import HttpResponse
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField
from django.shortcuts import render

from .models import Recruiter, MessageThread, JobPosting, Candidate
from .match_scores import calculate_match_score

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
        'score': calculate_match_score(thread.candidate, thread.job)
    }

    return render(request, 'inbox/thread.html', _context)


def posted_jobs(request):
    job_posting = JobPosting.objects.filter(recruiter=RECRUITER_ID).all()
    _context = {'title': "Djinni - Jobs", 'jobPosting': job_posting}

    return render(request, 'jobs/job_list.html', _context)


def jobs_candidates(request, pk):
    job = JobPosting.objects.filter(recruiter=RECRUITER_ID).get(id=pk)

    rated_threads = [
        {
            'thread': thread,
            'candidate': thread.candidate,
            'score': calculate_match_score(thread.candidate, job)
        }
        for thread in MessageThread.objects.filter(job=job.id)
    ]

    _context = {'title': "Djinni - Candidates",
                'job': job,
                'rated_threads': sorted(rated_threads, key=lambda x: x['score'], reverse=True)}

    return render(request, 'jobs/job_matches.html', _context)
