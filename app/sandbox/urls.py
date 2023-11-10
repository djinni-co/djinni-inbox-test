from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/inbox', permanent=False), name='root-redirect'),
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/<pk>/', views.inbox_thread, name='inbox_thread'),
    path('sort_by_score/', views.sort_by_score, name='sort_by_score'),
]
