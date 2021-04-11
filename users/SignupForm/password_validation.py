"""
Модуль с реализацией классов валидации 
поля password формы users.forms.SignupForm

Классы установлены вместо стандартных в перем. settings.AUTH_PASSWORD_VALIDATORS
"""

import re
from difflib import SequenceMatcher
from django.contrib.auth import password_validation
from django.core.exceptions import (
    FieldDoesNotExist, ValidationError,
)
from django.utils.translation import gettext as _, ngettext

class MinimumLengthValidator(password_validation.MinimumLengthValidator):

	def __init__(self, min_length=8):
		self.min_length = min_length

	def validate(self, password, user=None):
		if len(password) < self.min_length:
			raise ValidationError(_(f"Пароль слишком короткий. Он должен содержать не менее {self.min_length} символов."))

	def get_help_text(self):
		return _(f"Ваш пароль должен содержать не менее {self.min_length} символов.")
		

class UserAttributeSimilarityValidator(password_validation.UserAttributeSimilarityValidator):
	
	def validate(self, password, user=None):
		if not user:
			return
		
		for attribute_name in self.user_attributes:
			value = getattr(user, attribute_name, None)
			if not value or not isinstance(value, str):
				continue
			value_parts = re.split(r'\W+', value) + [value]
			for value_part in value_parts:
				if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:
					try:
						verbose_name = str(user._meta.get_field(attribute_name).verbose_name)
					except FieldDoesNotExist:
						verbose_name = attribute_name
					raise ValidationError(
						_("Пароль схож с %(verbose_name)s."),
						code='password_too_similar',
						params={'verbose_name': verbose_name},
					)
					
	def get_help_text(self):
		return _('Ваш пароль имеет сходство с персональными данными')
	