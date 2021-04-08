from django.urls import re_path, path

from . import views

app_name = 'menu'

urlpatterns = [
	path('', views.home, name='home'),
]