"""
Модуль с реализацией метода инициализации переменных
сессии
"""
from functools import wraps

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


"""
Перем. используется в декораторе
message_about_permission для устанавки
сообщения пользователю о доступе к 
запрашиваемому ресурсу при переходе
на веб-страницу.
"""
ACCESS_MESSAGES = {

	"admin": "Доступ к этому ресурсу есть только\
			  у пользователей, имеющие привелегии\
			  администратора. Поэтому, войдите\
			  на сайт как администратор, если\
			  учётные данные такого аккаута у\
			  Вас есть.",
							 
	"authenticated": "Доступ к этому ресурсу есть\
					  только у аутентифицированных\
					  пользователей."
}
									 
def message(user, status="sent"):
	"""
	Назначение: генерирование значения для установки 
				параметру 'message' объекта сессии 
				'account_verification'
				
	Принимает на вход экз. модели users.models.User (user) 
	и строку статуса успешности верификации аккаута (status), 
	по значению которой и определяется сообщение message.
	Значение объекта сессии message рендерится в шаблоне 
	login.html и информирует пользователя о состоянии
	верификации его аккаута.
	
	Возвращает строку сообщения.
	"""
	if not user and status == "fail":
		return "Эм, пользователь по какой-то причине был.\
				удалён.\
				С уважением, Mr.Smith"
	elif user and status == "fail":
		return "Ошибка подтверждения регистрации.\
				Нажмите кнопку \"отправить токен\", чтобы\
				получить код подтверждения заново.\
				С уважением, Mr.Smith"
	elif status == "success":
		return "Регистрация прошла успешно.\
				С уважением, Mr.Smith"
	return 'На почту {} была отправлена ссылка\
			для перехода подтверждения регистрации.\
			С уважением, Mr.Smith'.format(user.email)

def get_user_id(user):
	"""
	Назначение: Вспомогательный метод для опр. 
				id пользователя. Возвращаемое им 
				значение id устанавливается как 
				параметр url в шаблоне login.html
				для рендеринга кнопки повторной
				отправки письма пользователю, в случае,
				если он не получал письма или токен
				оказался недействителен после предыдущего
				запроса на верификацию аккаута.
	
	Принимает на вход экз. модели пользователя 
	users.models.User (user)
	
	Возвращает id пользователя в зашифрованном виде
	или None
	"""
	if user:
		return urlsafe_base64_encode(force_bytes(user.id))

def get_session_params(user, status="sent"):
	"""
	Назначение: опр. параметры объекта сессии 'account_verification'
	
	Принимает на вход экз. модели пользователя
	users.models.User (user) и статус верификации 
	аккаута (status)
	
	Статус верификации аккаута устанавливается кодом
	контроллеров и принимает значения:
	
		-- "sent" --- отправлено письмо с инструкцией 
					  верификации аккаута.
		-- "fail" --- верификация аккаута не удалась.
					  (нет пользователя в БД, недействителен 
					  уникальный ключ, отправленный для 
					  подтверждения аккаута)
		-- "success". --- верификация аккаута прошла
					      успешно.

	Возвращает словарь с переменными объекта сессии 'account_verification'
	"""
	return {"user_id": get_user_id(user), 
			"message": message(user, status), 
			"status": status}

def message_about_permission(p=5, access="admin"):
	"""
	Декоратор, применяемый к методу
	django.views.Views.no_permission_fail
	
	Устанавливает инф. сообщение в объект сессии
	'access' для пользователей, которые пытаются 
	запросить недоступный для них ресурс.
	
	p --- вр. действия объекта сессии в с.
	access --- тип доступа, опр. информацию 
	в шаблоне о доступе у определённых 
	групп пользователей
	"""
	
	def _message_about_permission(no_permission_fail):
		@wraps(no_permission_fail)
		def message(obj, request,):
			request.session["access"] = ACCESS_MESSAGES[access]
			request.session.set_expiry(p)
			return no_permission_fail(obj, request)
		return message
	return _message_about_permission
								