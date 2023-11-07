from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.db.models import Count, Q
from django.shortcuts import render, reverse


from .models import Recruiter, MessageThread, JobPosting

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

PER_PAGE = 5

def inbox(req):
    get_params = QueryDict('', mutable=True)
    get_params.update(req.GET)

    page = int(req.GET.get('page') or 1)
    sorting = req.GET.get('sort') or ''

    recruiter = Recruiter.objects.get(id = RECRUITER_ID)
    threads = MessageThread.objects.filter(
        recruiter = recruiter
    ).select_related('candidate', 'job')[
          (page - 1) * PER_PAGE
        : page * PER_PAGE
    ]

    context = {}

    get_params['page'] = page + 1
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
