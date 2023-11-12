from django.shortcuts import render

from .models import MessageThread
from .utils import get_context


def inbox(request):
    _context = get_context(request)
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
