from braces.views import GroupRequiredMixin
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView, redirect_to_login
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework.views import APIView

from . import account_confirmation as aconf
from . import get_session_params as session
from . import models
from .authentification import SecretKeyAuthentication
from .get_session_params import message_about_permission
from .forms import SignupForm, LoginForm
from .models import User
from .serializers import UserDataSerializer
from api_reqs_stat.models import ReqsStat
# Create your views here.

class LoginView(LoginView):

	"""
	Контроллер, обрабатывает форму
	входа пользователей и рендерит шаблон 
	login.html
	
	http://127.0.0.1:8000/accounts/login/
	"""
	
	form_class = LoginForm

class LogoutView(LogoutView):

	"""
	Контроллер, обрабатывает выход пользователя
	"""
	pass
	
class SignupView(FormView):

	"""
	Контроллер обрабатывает форму регистрации
	нового пользователя:
	
	http://127.0.0.1:8000/accounts/signup/
	"""
	
	form_class = SignupForm
	template_name = 'registration/register.html'

	def form_valid(self, form):	
		"""
		реализована логика отправки письма с
		инструкцией по верификации аккаута,
		реализована установка сообющеня пользователю
		в объект сессии об отправке письма с инструкцией
		по верификации аккаута
		"""
		if self.request.recaptcha_is_valid:
			user = aconf.create_unactive_user(form)
			aconf.send_message_to_activate(user)
			self.request.session['account_verification'] = session.get_session_params(user,)
			return redirect('user:login')
		return render(self.request, self.template_name, self.get_context_data())
			

class SendTokenAgain(View):
	
	"""
	Контроллер, осуществляет повторную отправку 
	письма пользователю с инструкцией по верификации
	аккаута. В переопр. методе 'get' реализовано оповещение
	об отправке письма, используя объект сессиии.
	"""
	
	def get(self, request, *args, **kwargs):
		user = aconf.get_user(kwargs['user_id'])
		if user:
			aconf.send_message_to_activate(user)
			request.session['account_verification'] = session.get_session_params(user,)
		return redirect('user:login')
	
	
class TokenVerification(View):

	"""
	Контроллер, осуществляющий отправку письма 
	пользователю с инструкцией по верификации
	аккаута. В переопр. методе 'get' реализовано оповещение
	о удачной/неудачной попытке верификации аккаута,
	используя объект сессии.
	"""

	def get(self, request, *args, **kwargs):
		user = aconf.get_user(kwargs['user_id'])
		request.session['account_verification'] = session.get_session_params(user, "fail")
		# если уник. ключ прошёл проверку и пользователь существует, то
		# производим активацию его аккаута:
		if user and aconf.is_right_token(user, kwargs['token']):
			user.is_active = True
			user.save()
			request.session['account_verification'] = session.get_session_params(user, "success")
		return render(request, 'registration/login.html', {'form': LoginForm()})


class Users(GroupRequiredMixin, View):

	"""
	Контроллер, обрабатывает страницу
	пользователей:
	
	https://127.0.0.1/accounts/users/
	
	Защищён от доступа со стороны пользователей, 
	не явл. администраторами
	"""
	
	group_required = (u"admins",)
	
	def get(self, request, *args, **kwargs):
		users = models.User.objects.all()
		users = [model_to_dict(user) for user in users]
		return render(request, 'users/users.html', {'users': users,})
	
	@message_about_permission(p=1, access="admin")
	def no_permissions_fail(self, request=None,):
		"""
		переопределение станд. метода для
		установки параметра сессии для оповещения 
		пользователя о доступе к ресурсу
		"""
		
		"""
		Called when the user has no permissions and no exception was raised.
		This should only return a valid HTTP response.
		By default we redirect to login.
		"""
	
		return redirect_to_login(request.get_full_path(),
								 self.get_login_url(),
								 self.get_redirect_field_name())
	

class ConfDeleteUsers(View):
	
	"""
	Контроллер, которому приходит список id пользователей
	модели users.models.User на удаление.
	
	На странице: 
	http://127.0.0.1:8000/accounts/confdeleteusers/
	
	рендерится диалоговое окно подтверждения удаления
	"""
	
	def post(self, request, *args, **kwargs):
		users_ids = self.request.POST.getlist('id')
		return render(request, 'users/confirm_del_users.html', {'users_ids': users_ids})
		
		

class DeleteUsers(View):

	"""
	Контроллер, обрабатывает данные пользователей,
	помеченные на удаление в форме шаблона users.html.
	
	Удаляет выбранных пользователей.
	"""
	
	def post(self, request, *args, **kwargs):
		users_ids = self.request.POST.getlist('id')
		deleting_users = User.objects.filter(pk__in=users_ids).delete()
		return redirect('user:users')


class UpdateUser(GroupRequiredMixin, UpdateView):

	"""
	Контроллер редактирует данные
	модели users.models.User
	
	Защищён от доступа со стороны пользователей, 
	не явл. администраторами
	
	http://127.0.0.1:8000/accounts/edit/pk/
	
	где pk --- id пользователя, целое число
	"""
	
	group_required = (u"admins",)
	model = User
	fields = ('username', 'email', 'phone', 'is_staff', 'is_active',)
	template_name_suffix = '_edit_form'
	success_url = reverse_lazy('user:users')
	


#Контроллеры для REST API:
		
class UserData(APIView):

	"""
	Контроллер отдаёт данные пользователя 
	по его username при авторизованном 
	http get-запросе:
	
	http://127.0.0.1:8000/accounts/rest_api/username/
	
	где username --- имя пользователя
	"""

	serializer = UserDataSerializer
	authentication_classes = (SecretKeyAuthentication,)
	http_method_names = ('get',)
	
	def get(self, request, username):
		user = User.objects.filter(username=username).first()
		serializer = UserDataSerializer(user)
		ReqsStat.objects.create(user=user, api_name='SUD')
		return Response(serializer.data)