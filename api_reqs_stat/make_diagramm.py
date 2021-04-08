# -*- coding: utf-8 -*-
"""
Модуль предназначен для вывода диаграммы 
числа запросов к функции REST API по конкретному
пользователю.

Модуль сохраняет диаграмму в файл *.jpg в папку
../media
"""

from collections import Counter
from datetime import datetime
import matplotlib
import matplotlib.dates
import matplotlib.ticker as ticker
import os
import pylab
from django.conf import settings

DEFAULT_DATE_NULL = [(datetime.now().date(), 0)]

def get_orded_dates_reqs(reqs):
	"""
	Принимает на вход список экз. кл. ReqsStat
	
	Возвращает упорядоченный список кортежей 
	из дат запросов и их частот. Список упорядочен
	по возрастанию частоты.
	"""
	dates = [req.request.date() for req in reqs]	
	dates = list(Counter(dates).items())
	dates.sort(key=lambda i: i[0])
	return dates
	
def get_datas_to_OX(dates):
	"""
	Принимает на вход упорядоченный список кортежей 
	из дат запросов и их частот.
	
	Возвращает список дат в целочисленном 
	представлении для библиотеки matplotlib.*
	"""
	dates = list(map(lambda i: i[0], dates + DEFAULT_DATE_NULL))
	return matplotlib.dates.date2num(dates)

def get_freqs_to_OY(dates):
	"""
	Принимает на вход упорядоченный список кортежей 
	из дат запросов и их частот.
	
	Возвращает список частот запросов по датам.*
	"""
	
	return list(map(lambda i: i[1], dates + DEFAULT_DATE_NULL))

def get_x_y(reqs,):
	"""
	Принимает на вход список экз. кл. ReqsStat.
	
	Возвращает два списка --- список дат и
	список частот запросов.
	
	
	* Порядок следования элементов в списках, возвращаемых
	методами get_datas_to_OX и get_datas_to_OX взаимно
	соотвествует.
	"""
	
	dates_ord = get_orded_dates_reqs(reqs)
	print("dates_ord", dates_ord)
	dates = get_datas_to_OX(dates_ord)
	freqs = get_freqs_to_OY(dates_ord)
	return dates, freqs

def get_filename(user_id, api_name,):
	"""
	Принимает на вход id пользователя (user_id)
	и имя функции REST API (api_name).
	
	Возвращает абсолютный путь к файлу
	вывода стат. данных о числе запросов к
	функции с именем api_name, совершённых
	пользователем с id user_id:
	
	"path_to_project\\media\\user_id_apiname.jpg",
	
	где path_to_project --- путь до папки проекта.
	"""
	
	return os.path.join('media', str(user_id) + api_name + ".jpg",)
	
def set_interval_OX(x):
	"""
	Процедура сдвига интервала по OX
	"""
	pylab.xlim(min(x)-1, max(x)+1)


def set_plot_settings(x):
	"""
	Процедура установки параметров графика:
	граф. интерфейс, формат данных и пр.
	"""
	matplotlib.use('Agg')
	axes = pylab.figure().gca()
	locator = matplotlib.dates.DayLocator()
	axes.xaxis.set_major_locator(locator)
	axes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y-%m-%d"))
	axes.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
	set_interval_OX(x)
	
def plot(reqs, user_id, api_name):
	"""
	Принимает на вход список экз. кл. ReqsStat (reqs)
	id пользователя (user_id) 
	и имя функции REST API (api_name).
	
	Отрисовывает график: 
	x=даты запросов, y=частота запросов
	и сохраняет его в формат *.jpg
	"""
	dates, freqs = get_x_y(reqs)
	set_plot_settings(dates)
	pylab.bar(dates, freqs,)
	pylab.grid()
	filename = get_filename(user_id, api_name,)
	pylab.savefig(filename, dpi=200, bbox_inches='tight')
	
if __name__ == "__main__":
	plot(reqs, user_id, api_name)
	