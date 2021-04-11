from django.urls import re_path, path

from . import views

app_name = 'secretkey'

urlpatterns = [
	path('secretkey/', views.generate_secret_key, name='secretkey'),
]