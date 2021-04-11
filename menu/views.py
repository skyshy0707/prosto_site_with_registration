from django.shortcuts import render
# Create your views here.


def home(request):
	"""
	Контроллер рендерит главную страницу
	
	https://127.0.0.1
	"""
	return render(request, 'menu/home.html',)

"""
Ниже реализованы контроллеры, рендерящие 
страницы обработчиков ошибок:
"""	

def handler404(request, exception=None):
    response = render(request, 'errors/error404.html', {})
    response.status_code = 404
    return response
 
 
def handler500(request):
    response = render(request, 'errors/error500.html', {})
    response.status_code = 500
    return response
	

def csrf_failure(request, exception=None):
    response = render(request, 'errors/error403.html', {})
    response.status_code = 403
    return response