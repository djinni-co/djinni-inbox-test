from django.http import HttpResponse
from django.db.models import Count, Q

from .models import JobPosting, Candidate, Recruiter, Message, MessageThread

def index(request):
    

    return HttpResponse("Hello, world.")
