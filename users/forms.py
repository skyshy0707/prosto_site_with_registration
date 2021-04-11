from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import EmailValidator
from django.forms import modelformset_factory
from django.utils.translation import ugettext, ugettext_lazy as _

from .models import User


class SignupForm(UserCreationForm):
	"""
	Модель формы, используемая в шаблоне register.html
	для заполнения данных пользователя при его регистрации
	"""
	
	email = forms.EmailField(validators=[EmailValidator("Недопустимый формат email")])
	error_messages = {'duplicate_username': _("Пользователь с таким именем уже есть"),
					  'password_mismatch': _("Пароли не совпадают"),}
					  
	
	class Meta:
		model = User
		fields = ('username', 'email', 'phone', 'password1', 'password2',)
		
		
class LoginForm(AuthenticationForm):

	"""
	Модель формы, используемая в шаблоне login.html
	для заполнения учётных данных пользователя при его 
	аутентификации
	"""
	
	error_messages = {
        'invalid_login': _("Некоррекнтые имя пользователя %(username)s и пароль. "
                           "Эти поля могут быть чувствительны к регистру."),
        'inactive': _("Ваш аккаут ещё не активирован."),
    }
	
	# перем., использующаяся в шаблоне входа на 
	# сайт login.html. 
	# Задаёт условие оповещения для пользователя об 
	# отправке письма на его email для верификации
	# его аккаута после того как он подтвердил
	# ввод пары (логин, пароль):
	# При значении по умолчанию пользователь не оповещается.
	alert_about_complete_reg = 0
	
	def get_user_from_tab(self, username):
		"""
		custom-метод, возращающий пользователя по
		username или None
		"""
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			user = None
		return user
	
	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		
		# пытаемся аутентифицировать пользователя при 
		# заполненных обязательных полях формы аутентификации:
		if username and password:
			self.user_cache = authenticate(self.request, 
										   username=username, 
										   password=password)
			# если аутентифицировать не получилось, зн.
			# делаем попытку проверки существует ли пользователь 
			# в таблице User
			if not self.user_cache:
				user = self.get_user_from_tab(username)
				# если пользователь существует и верны учётные данные, 
				# то делаем попытку проверить активирован ли пользователь:
				if user and user.check_password(password):
					self.confirm_login_allowed(user)
				# иначе --- вызываем исключение о неверных учётных данных:
				else:
					raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                        params={'username': self.username_field.verbose_name},
					)
		return self.cleaned_data
		
	def confirm_login_allowed(self, user):
	
		"""
		Дополнительная кастомизация:
		
		если было вызвано исключение о статусе 
		неактивации пользователя, то переопр. перем.
		alert_about_complete_reg = 1
		"""
		
		"""
		Controls whether the given User may log in. This is a policy setting,
		independent of end-user authentication. This default behavior is to
		allow login by active users, and reject login by inactive users.
		
		If the given user cannot log in, this method should raise a
		``forms.ValidationError``.
		
		If the given user may log in, this method should return None.
		"""
		if not user.is_active:
			self.alert_about_complete_reg = 1
			raise forms.ValidationError(
				self.error_messages['inactive'],
				code='inactive',
			)