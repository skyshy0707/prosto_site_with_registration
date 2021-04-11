from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render

from . import generate_secret_key as gkey
from .models import SecretKey

# Create your views here.


@login_required
def generate_secret_key(request):
	"""
	Контроллер, рендерит страницу
	https://127.0.0.1/secretkey
	на которой аутентифицированный пользователь
	видит свой уникальный токен, с помощью
	которого осуществляется доступ к REST API
	
	В контекст передаётся secretkey, значение которого ---
	16-ичное незашифрованное число, записанное в перем. key
	
	Доступ к странице контроллер разрешает при авторизации.
	"""
	key = gkey.generate_key()
	xkey = gkey.get_xkey_value(key)
	try:
		secret_key = SecretKey.objects.create(user=request.user,
											  xkey=xkey)
	except IntegrityError as e:
		while True:
			try:
				key = gkey.generate_key()
				SecretKey.objects.filter(user=request.user).update(
					xkey=gkey.get_xkey_value(key)
				)
				break
			except IntegrityError as e:
				continue
			
	return render(request, 'secretkey/secret_key.html', {'secretkey': key})
	
