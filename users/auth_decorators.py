"""
Модуль предназначен для проверки авторизации
пользователей для доступа к страницам, доступных
только для авторизированных пользователей.
"""

from django.shortcuts import redirect
from .clear_sessions_params import clear_session_params


def is_auth(request):
	"""
	Предназначен для проверки авторизации пользователя.
	Метод используется в login_required --- см. ниже.
	"""
	try:
		user = request.user.authenticated
	except AttributeError:
		user = None
	return user

def login_required(view_func):
	"""
	Декоратор, предназначенный для проверки доступа к
	странице по условию авторизован ли пользователь, 
	осуществеляющий доступ к странице.
	
	Также, в начале производит очистку данных сессии, 
	которые относятся к контроллеру с другими привелегиями.
	"""
	
	def view_func(request, *args, **kwargs):
		clear_session_params(request, 'admin_access_only',)
		if not is_auth(request):
			return redirect('user:login')
		return view_func(request, *args, **kwargs)
	return view_func
	
