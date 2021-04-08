from braces.views import GroupRequiredMixin
from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, redirect_to_login
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect
from django.views import View
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework.views import APIView

from api_reqs_stat.models import ReqsStat
from .authentification import SecretKeyAuthentication
from .forms import SignupForm, LoginForm, UserForm, UserFormset
from .serializers import UserDataSerializer
from . import email_confirmation as econf
from . import get_session_params as session
from . import models 
# Create your views here.


class LoginView(LoginView):

	"""
	Контроллер, обрабатывающий форму
	входа пользователей и рендерящий шаблон 
	login.html
	
	http://127.0.0.1:8000/accounts/login/
	"""
	
	form_class = LoginForm
	'''success_url = 'menu:home'''


	'''def get(self, request):
		return render(request, 'registration/login.html', {'form': LoginForm()})'''
	
	'''def form_invalid(self, form):
		try:
			form.clean()
		except forms.ValidationError:
			return render(self.request,
						  'registration/login.html',
						  {'form': form,})
			 
		login(self.request, form.get_user())
		
		return redirect('menu:home')'''
	
	'''def post(self, request):
		form = LoginForm(request, data=request.POST)
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)
			
		return render(request, 'registration/login.html', {'form': form})'''

class LogoutView(LogoutView):

	"""
	Контроллер, обрабатывающий выход пользователя
	"""
	pass
	
	'''def redirect_to_response(self, context):
		return redirect('menu:home',)
		
	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		return self.redirect_to_response(context)'''


class SignupView(FormView):

	"""
	Контроллер обрабатыващий форму регистрации
	нового пользователя:
	
	http://127.0.0.1:8000/accounts/signup/
	"""
	
	form_class = SignupForm
	template_name = 'registration/register.html'

	def form_valid(self, form):	
		"""
		реализована логика отправки письма с
		инструкцией верификации аккаута,
		реализована установка сообющеня пользователю
		в объект сессии об отправке письма с инструкцией
		по верификации аккаута
		"""
		if self.request.recaptcha_is_valid:
			user = econf.create_unactive_user(form)
			econf.send_message_to_activate(user)
			self.request.session['params'] = session.get_session_params(user,)
			return redirect('user:login')
		return render(self.request, self.template_name, self.get_context_data())
			
	'''def post(self, request, *args, **kwargs):
		
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form)
		return render(request, self.template_name, self.get_context_data())'''
	

class SendTokenAgain(View):
	
	"""
	Контроллер, осуществляющий повторную отправку 
	письма пользователю с инструкцией по верификации
	аккаута. В переопр. методе get реализовано оповещение
	об отправке письма, используя объект сессиии.
	"""
	
	def get(self, request, *args, **kwargs):
		user = econf.get_user(kwargs['user_id'])
		if user:
			econf.send_message_to_activate(user)
			request.session['params'] = session.get_session_params(user,)
		return redirect('user:login')
	
	
'''def send_token_again(request, user_id):
	
	if request.method == 'GET':
		user = econf.get_user(user_id)
		if user:
			token = econf.get_conf_token(user)
			econf.redirect_link(user, token)
			request.session['params'] = econf.get_session_params(user,)
			return redirect('user:login')
	return render(request, 'page405.html',)'''
	
class TokenVerification(View):

	"""
	Контроллер, осуществляющий отправку письма 
	пользователю с инструкцией по верификации
	аккаута. В переопр. методе get реализовано оповещение
	о удачной/неудачной попытке верификации аккаута,
	используя объект сессии.
	"""

	def get(self, request, *args, **kwargs):
		user = econf.get_user(kwargs['user_id'])
		request.session['params'] = session.get_session_params(user, "fail")
		print("session parameters", session.get_session_params(user, "fail"))
		print("user", user)
		# если уник. ключа прошёл проверку и пользователь существует, то
		# производим активацию его аккаута:
		if user and econf.is_right_token(user, kwargs['token']):
			user.is_active = True
			user.save()
			request.session['params'] = session.get_session_params(user, "success")
		return render(request, 'registration/login.html', {'form': LoginForm()})

'''
def token_verification(request, user_id, token, status=0):
	
	if request.method == 'GET':
		user = econf.get_user(user_id)
		request.session['params'] = econf.get_session_params(user, "fail")

		if user and econf.is_right_token(user, token):
			user.is_active = True
			user.save()
			request.session['params'] = econf.get_session_params(user, "success")
		return render(request, 'registration/login.html', {'form': LoginForm(),})
	return render(request, 'page405.html',)'''
		

class Users(GroupRequiredMixin, View):

	"""
	Контроллер, обрабатывающий страницу
	пользователей:
	
	https://127.0.0.1/accounts/users/
	
	Защищён от доступа со стороны пользователей, 
	не явл. администраторами
	"""
	
	group_required = (u"admins",)
	
	def get(self, request, *args, **kwargs):
		users = models.User.objects.all()
		users = [model_to_dict(user) for user in users]
		return render(request, 'users.html', {'users': users,})
	
	def no_permissions_fail(self, request=None):
		"""
		Called when the user has no permissions and no exception was raised.
		This should only return a valid HTTP response.
		By default we redirect to login.
		"""
		request.session["admin_access_only"] = "Доступ к ресурсу только у\
												аккаутов, имеющих привелегии\
												администратора. Поэтому войдите\
											    на сайт как администратор, если\
												учётные данные такого аккаута у\
												Вас есть."
		return redirect_to_login(request.get_full_path(),
								 self.get_login_url(),
								 self.get_redirect_field_name())
	


	
class ConfDeleteUsers(View):
	
	"""
	Контроллер, обрабатывающий формы пользователей
	users.forms.UserFormset, помеченные на удаление.
	
	На странице: 
	http://127.0.0.1:8000/accounts/confdeleteusers/
	
	рендерится диалоговое окно подтверждения удаления
	"""
	
	def post(self, request, *args, **kwargs):
		users_ids = self.request.POST.getlist('id')
		return render(request, 'confirm_del_users.html', {'users_ids': users_ids})
		
		

class DeleteUsers(View):

	"""
	Контроллер, обрабатывающий формы пользователей
	users.forms.UserFormset, помеченные на удаление.
	
	Удаляет выбранных пользователей.
	"""
	
	def post(self, request, *args, **kwargs):
		users_ids = self.request.POST.getlist('id')
		deleting_users = User.objects.filter(pk__in=users_ids).delete()
		return redirect('user:users')


class UpdateUser(GroupRequiredMixin, UpdateView):

	"""
	Контроллер, обрабатывающий форму
	пользователя при редактировании его
	данных.
	
	Защищён от доступа со стороны пользователей, 
	не явл. администраторами
	
	http://127.0.0.1:8000/accounts/edit/pk/
	
	где pk --- id пользователя, целое число
	"""
	
	group_required = (u"admins",)
	model = models.User
	fields = ('username', 'email', 'phone', 'is_staff', 'is_active',)
	template_name_suffix = '_edit_form'
	success_url = reverse_lazy('user:users')
	


#Контроллеры для REST API:
		
class UserData(APIView):

	"""
	Контроллер, предназначенный для отдачи
	данных пользователя по его username при 
	авторизованном http get-запросе.
	
	
	"""

	serializer = UserDataSerializer
	authentication_classes = (SecretKeyAuthentication,)
	http_method_names = ('get',)
	
	def get(self, request, username):
		user = User.objects.filter(username=username).first()
		serializer = UserDataSerializer(user)
		ReqsStat.objects.create(user=user, api_name='SUD')
		return Response(serializer.data)