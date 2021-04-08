from django.urls import re_path, path

from . import views

app_name = 'api_reqs_stat'

urlpatterns = [
	path('user_api_reqs_stat/<int:pk>', views.APIRequestsStat.as_view(), name='stat'),
]