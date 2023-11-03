from django.http import HttpResponse
from django.db.models import Count, Q
from django.shortcuts import render

from .models import JobPosting, Candidate, Recruiter, Message, MessageThread

def index(request):
    return render(request, 'inbox/chats.html', { 'title': "Djinni - Inbox" })
