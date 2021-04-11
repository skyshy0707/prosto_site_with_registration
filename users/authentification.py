"""
Модуль аутентификации пользователей 
в REST API сайта
"""

import datetime
from django.contrib.auth.models import User
from django.middleware.csrf import CsrfViewMiddleware
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from secretkey.generate_secret_key import get_xkey_value
from secretkey.models import SecretKey

class CSRFCheck(CsrfViewMiddleware):
	"""
	Класс, используемый для проверки csrf-токена
	"""
	def _reject(self, request, reason):
		# вместо HttpResponse возвращает причину запрещения доступа
		return reason
		
		
class SecretKeyAuthentication(BaseAuthentication):
	"""
	Класс, используемый для аутентификации
	пользователей для доступа к REST API.
	
	Задан в качестве класса по умолчанию
	в переменной settings.REST_FRAMEWORK
	в качестве класса аутентификации по 
	умолчанию
	"""
	
	#срок действия токена доступа в ч:
	validity = datetime.timedelta(hours=64)
	
	
	def authenticate(self, request):
		
		#проверка наличия необходимых  заголовков:
		authorization_header = request.headers.get('Authorization')
		
		if not authorization_header:
			return None
		try:
			access_key = authorization_header.split(' ')[1]
		except IndexError:
			raise exceptions.AuthenticationFailed('Key prefix missing')
		
		
		#проверка срока дейтствия и наличия токена доступа:
		secretkey = SecretKey.objects.filter(xkey=get_xkey_value(access_key)).first()
		if not secretkey or (secretkey.created + self.validity) < timezone.now():
			raise exceptions.AuthenticationFailed('access_token expired')
		
		#проверка статуса активации пользователя:
		user = secretkey.user
		
		if not user.is_active:
			raise exceptions.AuthenticationFailed('user is inactive')
		
		#проверка валидации csrf-токена:
		self.enforce_csrf(request)
		return (user, None)
		
	def enforce_csrf(self, request):
		"""
		Принудительная проверка CSRF
		"""
		check = CSRFCheck()
		# помещаем request.META['CSRF_COOKIE'], что будет использоваться в process_view():
		check.process_request(request)
		reason = check.process_view(request, None, (), {})
		print(reason)
		if reason:
			# если ошибка CSRF --- вызываем сообщение об ошибке:
			raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)