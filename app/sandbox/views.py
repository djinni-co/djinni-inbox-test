from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.db.models import Count, Q
from django.shortcuts import render, reverse

from . import constants as C

from .models import Recruiter, MessageThread, JobPosting

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

def inbox(req):
    get_params = QueryDict('', mutable=True)
    get_params.update(req.GET)

    page = int(req.GET.get(C.inbox.http.param.PAGING) or 1)
    sorting = req.GET.get(
        C.inbox.http.param.SORTING
    ) or C.inbox.sorting.DEFAULT

    recruiter = Recruiter.objects.get(id = RECRUITER_ID)
    threads = MessageThread.objects.filter(
        recruiter = recruiter
    ).select_related('candidate', 'job')[
          (page - 1) * C.inbox.paging.PER_PAGE
        : page * C.inbox.paging.PER_PAGE
    ]

    context = { 'const': C.inbox }

    context |= {
        'sorting_options': C.inbox.sorting.LIST,
        'current_sorting': sorting,
    }

    get_params[C.inbox.http.param.PAGING] = page + 1
    context |= {
        'next_page_url': '%s?%s' % (
            reverse('sb:inbox'),
            get_params.urlencode(),
        ),
    }

    context |= {
        'jobs': JobPosting.objects.filter(
            recruiter = recruiter
        ).all()
    }

    context |= {
        'title': "Djinni - Inbox",
        'recruiter': recruiter,
        'threads': threads,
    }

    template = 'inbox/chats.html'
    if req.headers.get('Hx-Request') == 'true':
        template = 'inbox/mixin/chat-list.jinja'

    return render(req, template, context)

def inbox_thread(req, pk):
    thread = MessageThread.objects.get(id = pk)
    messages = thread.message_set.all().order_by('created')

    context = {
        'pk': pk,
        'title': "Djinni - Inbox",
        'thread': thread,
        'messages': messages,
        'candidate': thread.candidate,
    }

    return render(req, 'inbox/thread.html', context)
