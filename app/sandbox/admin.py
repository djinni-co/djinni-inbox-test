from django.contrib import admin

from . import models as M

# Register your models here.

admin.site.register(M.Candidate)
admin.site.register(M.Recruiter)
admin.site.register(M.JobPosting)
admin.site.register(M.Message)
admin.site.register(M.MessageThread)
