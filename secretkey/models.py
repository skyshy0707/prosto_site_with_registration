from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.


class SecretKey(models.Model):
	"""
    Модель, предназначенная для хранения токена доступа
	к REST API в БД в зашифрованном виде.
	
	Поле created используется при проверке
	срока токена, по которому клиент осуществляет доступ
	к REST API.
    """
	
	xkey = models.CharField(_("XKey"), max_length=40, primary_key=True,)
	user = models.OneToOneField(
		User, related_name='secret_key',
		on_delete=models.CASCADE, verbose_name=_("User"),
	)
	created = models.DateTimeField(_("Created"), auto_now_add=True)
	
	class Meta:
		# Work around for a bug in Django:
		# https://code.djangoproject.com/ticket/19422
		#
		# Also see corresponding ticket:
		# https://github.com/encode/django-rest-framework/issues/705
		abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS
		verbose_name = _("SecretKey")
		verbose_name_plural = _("SecretKeys")
	
		
	def save(self, *args, **kwargs):
		return super().save(*args, **kwargs)
	
	
	def __str__(self):
		return self.xkey
		
admin.site.register(SecretKey,)