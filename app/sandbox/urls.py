from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
	path('', RedirectView.as_view(url='/inbox', permanent=False), name='root-redirect'),
  path('inbox/', views.inbox, name='inbox'),
  path('jobs/', views.jobs, name='jobs'),
  path('jobs_candidates/<pk>/', views.jobs_candidates, name='jobs_candidates'),
  path('inbox/<pk>/', views.inbox_thread, name='inbox_thread'),
]
