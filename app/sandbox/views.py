from django.http import HttpResponse
from django.db.models import Count, Q
from django.shortcuts import render


from .models import JobPosting, Recruiter, MessageThread
from .scoring_algorithm import calc_score

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

def inbox(request):
    recruiter = Recruiter.objects.get(id = RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter = recruiter).select_related('candidate', 'job')

    _context = { 'title': "Djinni - Inbox", 'recruiter': recruiter, 'threads': threads }

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
        'score': calc_score(thread),
    }

    return render(request, 'inbox/thread.html', _context)


def jobs_list(request):
    jobs = JobPosting.objects.filter(recruiter_id=RECRUITER_ID).all()
    _context = {'title': 'Djinni - Jobs', 'jobs': jobs}

    return render(request, 'jobs/job_post.html', _context)


def job_candidates(request, pk):
    job = JobPosting.objects.get(id=pk, recruiter_id=RECRUITER_ID)

    threads_data = [
        {'thread': thread, 'score': calc_score(thread)}
        for thread in job.messagethread_set.all()
    ]

    _context = {
        'title': 'Djinni - Candidates',
        'job': job,
        'threads_data': sorted(threads_data, key=lambda x: x['score'], reverse=True),
    }

    return render(request, 'jobs/job.html', _context)
