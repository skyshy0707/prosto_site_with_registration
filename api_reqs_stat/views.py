from braces.views import GroupRequiredMixin
from . import make_diagramm as md
from django.shortcuts import render, redirect
from django.views import View
from .forms import SelectAPI
from .models import ReqsStat
from .api_settings import API_NAMES
# Create your views here.


class APIRequestsStat(GroupRequiredMixin, View):

	group_required = (u"admins",)
	"""
	Класс контроллера, рендерящий страницу
	статистики запросов к функции REST API
	по конкретному пользователю c id=pk:
	
	home.ru/user_api_reqs_stat/pk
	"""
	
	def get(self, request, *args, **kwargs):
		"""
		На странице:
		home.ru/user_api_reqs_stat/pk
		рендерится форма api_reqs_stat.forms.SelectAPI 
		с полем выпадающего списка функций REST API
		"""
		return render(request, 'select_api.html', {'form': SelectAPI(),
												   'user_id': kwargs['pk']})
		
	
	def post(self, request, *args, **kwargs):
		"""
		После подтверждения выбора функции REST API на странице:
		home.ru/user_api_reqs_stat/pk
		рендерится диаграмма частоты запросов по датам
		к функции REST API по конкретному пользователю
		
		В контекст передаётся абс. путь к файлу диаграммы 'file' 
		и название функции REST API api_name (не код)
		"""
		
		form = SelectAPI(request.POST)
		if form.is_valid():
			user_id = kwargs['pk']
			api_name = form.cleaned_data['api_name']
			context = {'file': md.get_filename(user_id, api_name),
					   'api_name': dict(API_NAMES)[api_name],}
					   
			reqs = ReqsStat.objects.filter(user__id=user_id,
										   api_name=api_name,)	
										   
			md.plot(reqs, user_id, api_name)
			return render(request, 'draft_api_reqs_stat.html', context)
			
		return redirect('api_reqs_stat:stat', user_id)
			
			


