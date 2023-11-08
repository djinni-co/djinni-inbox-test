import os

from django.shortcuts import render

from .analyzator import Analyzator

from .models import Recruiter, MessageThread, JobPosting

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

faiss_index_path = "faissIDMap.index"
analyzator = Analyzator()
analyzator.read_faiss_index(faiss_index_path)

TEST_THREAD_INDEX = 0  # needed to select job posting for test

def inbox(request):
    recruiter = Recruiter.objects.get(id = RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter = recruiter).select_related('candidate', 'job')

    # Needed to match faiss index ids (check create_faiss_index func)
    threads = sorted(threads, key=lambda x: x.candidate.name, reverse=False)

    # Uncomment these lines to create new faiss index
    # if os.path.exists(faiss_index_path) is False:
    #   analyzator.create_faiss_index(threads, faiss_index_path)

    # Inbox based on recruiter-candidate communication
    # but we need to select job for candidates search
    selected_job = threads[TEST_THREAD_INDEX].job
    print("SELECTED JOB: \n", selected_job.long_description)
    ####

    distances, indices = analyzator.faiss_search(selected_job, k=1000)
    threads = list(map(threads.__getitem__, indices[0]))

    threads = map(lambda x:x[1], sorted(enumerate(threads), key=lambda x: distances[0][x[0]], reverse=False)) # sort threads by distance

    _context = { 'title': "Djinni - Inbox", 'recruiter': recruiter, 'threads': threads }

    return render(request, 'inbox/chats.html', _context)

def inbox_thread(request, pk):
    thread = MessageThread.objects.get(id = pk)
    messages = thread.message_set.all().order_by('created')

    similarity = analyzator.get_candidate_job_similarity(thread)

    _context = {
        'pk': pk,
        'title': "Djinni - Inbox",
        'thread': thread,
        'messages': messages,
        'candidate': thread.candidate,
        'similarity': similarity,
    }

    return render(request, 'inbox/thread.html', _context)
