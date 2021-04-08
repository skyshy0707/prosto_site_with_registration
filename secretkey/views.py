from django.db import IntegrityError
from django.shortcuts import render
from users.auth_decorators import login_required
from .models import SecretKey
from . import generate_secret_key as gkey
# Create your views here.


@login_required
def generate_secret_key(request):
	"""
	Контроллер, рендерит страницу
	home.ru/secretkey
	на которой аутентифицированный пользователь
	видит свой уникальный токен, с помощью
	которого осуществляется доступ к REST API
	
	В контекст передаётся secretkey, значение которого
	16-ичное незашифрованное число, записанное в перем. key
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
			
	return render(request, 'secret_key.html', {'secretkey': key})
	
