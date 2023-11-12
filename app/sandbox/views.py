from django.http import HttpResponse
from django.db.models import Count, Q
from django.shortcuts import render


from .models import Recruiter, MessageThread

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

def inbox(request):
    """
       Retrieves and displays recruiter's inbox with sorted message threads.

       :param request: HTTP request object.
       :return: Rendered inbox template.
    """
    recruiter = Recruiter.objects.get(id=RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter=recruiter).select_related('candidate', 'job')
    sort_by = request.GET.get('sort', 'default')

    if sort_by == 'score':
        threads = threads.order_by('-score')
    elif sort_by == 'created':
        threads = threads.order_by('-created')


    _context = {'title': "Djinni - Inbox", 'recruiter': recruiter, 'threads': threads}

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
