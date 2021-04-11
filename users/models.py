import binascii
import os

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.SignupForm.field_validators import (validate_format_username, 
											   validate_format_phone)
# Create your models here.

class User(AbstractUser):
	
	username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
		validators=[validate_format_username],
        help_text=_('До 150 символов. Допустимые символы --- буквы, цифры или @/./+/-/_ only.'),
    )
	
	email = models.EmailField(_('email address'), blank=True, unique=True)
	
	phone = models.CharField(
		max_length=200, 
		validators=[validate_format_phone],
		help_text=_('До 200 символов. Допустимый формат: +XXX...XXX, XXX...XXX'),
	)
	
	
class VerificationCode(models.Model):
	"""
	Модель создана по прототипу модели
	токена авторизации:
	https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/models.py
    The default authorization token model.
    """
	key = models.CharField(_("Key"), max_length=40, primary_key=True)
	user = models.OneToOneField(
		User, related_name='verification_code',
		on_delete=models.CASCADE, verbose_name=_("User")
	)
	created = models.DateTimeField(_("Created"), auto_now_add=True)
	
	class Meta:
		# Work around for a bug in Django:
		# https://code.djangoproject.com/ticket/19422
		#
		# Also see corresponding ticket:
		# https://github.com/encode/django-rest-framework/issues/705
		abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS
		verbose_name = _("VerificationCode")
		verbose_name_plural = _("VerificationCodes")
		
	def save(self, *args, **kwargs):
		return super().save(*args, **kwargs)
		
	@classmethod
	def generate_key(cls):
		return binascii.hexlify(os.urandom(30)).decode()
	
	def __str__(self):
		return self.key
		
admin.site.register(VerificationCode)
admin.site.register(User)