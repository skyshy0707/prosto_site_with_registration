"""
Модуль с реализацией метода очистки сессий
"""

def clear_session_params(request, *args):
	
	for par in args:
		request.session[par] = {}
