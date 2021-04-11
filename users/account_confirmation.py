"""
Модуль используется для отправки пользователю
письма с инструкцией по верификации аккаута и
готовит для этого необходимые данные.
"""

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.shortcuts import reverse
from django.template.loader import get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .models import VerificationCode as VCode
from .models import User
from secretkey.generate_secret_key import generate_key



def create_unactive_user(form):
	"""
	Назначение: создаёт экз. модели 
				users.models.User
				со статусом is_active = False
	
	Принимает на вход экз. класса формы 
	users.forms.SignupForm c queryset полей 
	модели users.models.User
	
	Возвращает экз. модели users.models.User
	"""
	user = form.save(commit=False)
	user.is_active = False
	user.save()
	return user


def get_user(user_id):
	"""
	Назначение: получает пользователя
				из БД по зашифрованному id из 
				http-запроса на верификацию аккаута
	
	Принимает на вход id модели users.models.User 
	user_id в зашифрованном виде
	
	Возвращает объект модели users.models.User 
	или None если пользователь не существует
	"""
	user_id = force_bytes(urlsafe_base64_decode(user_id))
	try:
		user = User.objects.get(pk=user_id)
	except User.DoesNotExist:
		return None
	return user
	
def get_conf_token(user):
	"""
	Назначение: генерирует для пользователя
				уникальный ключ token, используемый
				для подтверждения пользователя
	
	Принимает на вход экз. модели users.models.User
	
	Вовзращает уникальный ключ (строка)
	"""
	key = generate_key(length=30)
	try:
		token = VCode.objects.create(user=user,
								     key=key)
	except IntegrityError as e:
		while True:
			try:
				VCode.objects.filter(user=user).update(
					key=generate_key(length=30)
				)
				token = VCode.objects.filter(user=user).first()
				break
			except IntegrityError as e:
				continue
	return token
	
def is_right_token(user, sent_token):
	"""
	Назначение: Проверка правильности уникального ключа
				верификации аккаута
	
	Принимает на вход экз. модели users.models.User (user) 
	и уникальный ключ из http-запроса от клиента (sent_token)
	
	Возвращает условие равенства уник. ключа из запроса и
	значения, хранящегося в БД.
	"""
	
	token, _ = VCode.objects.get_or_create(user=user)
	return token.key == sent_token
	
											
def create_template_for_req_user(redirect_link):
	"""
	Декоратор, создающий шаблон для отправки 
	письма клиенту на подтверждение верификации аккаута
	
	Оборачивает метод создания ссылки redirect_link, 
	по которой переходит клиент для подтверждения аккаута
	
	Возвращает объект кл. django.template.Template
	"""
	def template(user, token):
		url = redirect_link(user, token)
		template = get_template('users/confirm_user.html')
		return template.render({'redirect_link': url,
								'username': user.username})
								
	template.__doc__ = redirect_link.__doc__
	template.__name__ = redirect_link.__name__
	return template


def send_template(message):
	"""
	Декоратор, отправляющий шаблон письма клиенту
	
	Оборачивает метод create_template_for_req_user,
	который возвращает шаблон письма
	"""
	def send(user, token):
		mail = EmailMessage('подтверждение аккаута', 
							message(user, token), 
							to=[user.email], 
							from_email=settings.EMAIL_HOST_USER)
		mail.content_subtype = 'html'
		mail.send()
		
	send.__doc__ = message.__doc__
	send.__name__ = message.__name__
	return send

@send_template
@create_template_for_req_user	
def redirect_link(user, token):
	"""
	Метод, генерирующий ссылку по которой переходит
	клиент для подтверждения аккаута
	
	Принимает на вход экз. модели users.models.User 
	(user) и сгенерированный уникальный ключ (token).
	
	Возвращает строку в формате:
	
	http://site.ru/accounts/login/user_id/token/
	"""
	user_id = urlsafe_base64_encode(force_bytes(user.id))
	return 'http://localhost:8000' + reverse('user:token_verification', 
											 kwargs={'user_id': user_id,
													 'token': token,})

def send_message_to_activate(user):
	"""
	Процедура, вызывающая в своём теле 
	метод генерирования уникального ключа 
	и отправляющая письмо клиенту на email 
	с инструкцией по верификации акаута
	
	Используется в контроллерах 
	users.views.SendTokenAgain,
	users.views.TokenVerification,
	users.views.SignupView
	"""
	token = get_conf_token(user)
	redirect_link(user, token)											