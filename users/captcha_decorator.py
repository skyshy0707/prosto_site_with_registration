"""
Модуль с реализацией проверки каптчи
"""

from django.conf import settings
from django.contrib import messages

import requests


def check_recaptcha(function):
	"""
	Декоратор, используемый для оборачивания контроллера,
	отвечающего за рендеринг страницы регистрации нового
	пользователя с формой регистрации данных.
	
	
	Схема проверки:
	
	1) Анализируем ответ google-сервера о валидации каптчи
	recaptcha_response, в поле 'g-recaptcha-response'
	
	2) Посылаем данные recaptcha_response и секретный ключ
	settings.GOOGLE_RECAPTCHA_SECRET_KEY
	
	3) Получаем финальный ответ от google-сервера о валидации
	каптчи, содержащийся в поле 'success'
	"""
	def wrap(request, *args, **kwargs):
		request.recaptcha_is_valid = None
		if request.method == 'POST':
			recaptcha_response = request.POST.get('g-recaptcha-response')
			data = {
				'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
				'response': recaptcha_response
			}
			r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
			result = r.json()
			if result['success']:
				request.recaptcha_is_valid = True
			else:
				request.recaptcha_is_valid = False
				messages.error(request, 'Invalid reCAPTCHA. Please try again.')
		return function(request, *args, **kwargs)

	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap