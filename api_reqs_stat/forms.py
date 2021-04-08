from django import forms
from .api_settings import API_NAMES


class SelectAPI(forms.Form):
	"""
	Класс формы выбора функции REST API_NAMES
	
	Используется в представлении, выводящее 
	стат. числа запросов к REST API
	"""
	api_name = forms.CharField(widget=forms.Select(choices=API_NAMES))