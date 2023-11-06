from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/inbox', permanent=False), name='root-redirect'),
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/<pk>/', views.inbox_thread, name='inbox_thread'),

    path('my_jobs/', views.job_postings, name='job_postings'),
    path('my_jobs/<pk>/', views.job_post_threads, name='job_post_threads'),
]
