"""
Модуль с реализацией методов валидации 
полей phone, username формы users.forms.SignupForm
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, ugettext_lazy as _



def validate_format_username(value):

	if not re.fullmatch("[\s\w.@+-]+", value):
		raise ValidationError(_("Недопустимое имя пользователя: %s"),
							  params=(value,))
	return value
	
def validate_format_phone(value):
	phone_num = value.split("+")[-1]
	
	try:
		int(phone_num)
	except ValueError:
		raise ValidationError(_("Недопустимый номер телефона: %s"),
							  params=(phone_num,))
	return value
		