from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('inbox/', views.index, name='index'),
	path('', RedirectView.as_view(url='/inbox', permanent=False), name='root-redirect'),
	path('', RedirectView.as_view(url='/inbox', permanent=False), name='root-redirect'),
]
