"""
Модуль предназначен для хранения переменных.

Переменные используются для задания значения поля 
мультивыбора функции REST API.

Поле используется в классе формы и модели:
 --api_reqs_stat.forms.SelectAPI
 --api_reqs_stat.models.ReqsStat
"""

SIMPLE_USER_DATA = 'SUD'

#Список названий функций REST API в виде
#последовательности кортежей (код, имя_функции_REST_API):
API_NAMES = [
	(SIMPLE_USER_DATA, 'Simple User Data'),
]