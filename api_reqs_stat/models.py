from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .api_settings import API_NAMES, SIMPLE_USER_DATA
from users.models import User

# Create your models here.

class ReqsStat(models.Model):

	"""
	Класс модели, который учитывает статистику запросов 
	к функции REST API. Код функции задаётся в поле api_name.
	"""
	
	SIMPLE_USER_DATA = SIMPLE_USER_DATA
	API_NAMES = API_NAMES
	
	user = models.ForeignKey(User, 
							 related_name='api_reqs_stat',
							 on_delete=models.CASCADE, 
							 verbose_name=_("User"),)
							 
	api_name = models.CharField(max_length=3,
								choices=API_NAMES,
								default=SIMPLE_USER_DATA,)
	
	request = models.DateTimeField(_("Requested"), auto_now_add=True)
	
	
admin.site.register(ReqsStat,)							 

