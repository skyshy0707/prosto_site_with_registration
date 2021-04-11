from django import forms

from .api_settings import API_NAMES


class SelectAPI(forms.Form):
	"""
	Назначение класса --- выбор имени функции REST API
	для просмотра статистики числа запросов.
	
	Используется в представлении users.views.UserData, 
	выводящее статистику числа запросов к REST API
	"""
	api_name = forms.CharField(widget=forms.Select(choices=API_NAMES))