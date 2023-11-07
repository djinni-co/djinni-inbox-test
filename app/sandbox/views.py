import os

from django.shortcuts import render

from .analyzator import Analyzator

from .models import Recruiter, MessageThread

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

faiss_index_path = "faissIndexIDMap3.index"
analyzator = Analyzator()

def inbox(request):
    recruiter = Recruiter.objects.get(id = RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter = recruiter).select_related('candidate', 'job')

    threads = sorted(threads, key=lambda x: analyzator.calc_priority(x), reverse=False)

    # Only during first run and creates faiss index
    if os.path.exists(faiss_index_path) is False:
        analyzator.create_faiss_index(threads, faiss_index_path)

    analyzator.read_faiss_index(faiss_index_path)
    # D, I = analyzator.faiss_search(threads[0].job.long_description)
    # print(I)

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
