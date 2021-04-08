from django.urls import re_path, path
from . import views
from .captcha_decorator import check_recaptcha
app_name = 'user'

urlpatterns = [
	path('signup/', check_recaptcha(views.SignupView.as_view()), name='signup'),
	path('users/', views.Users.as_view(), name='users',),
	path('confdeleteusers/', views.ConfDeleteUsers.as_view(), name='conf_delete_users',),
	path('deleteusers/', views.DeleteUsers.as_view(), name='delete_users',),
	path('edit/<int:pk>/', views.UpdateUser.as_view(), name='edit_user',),
	path('login/', views.LoginView.as_view(), name='login'),
	path('logout/', views.LogoutView.as_view(), name='logout'),
	path('login/<str:user_id>/', views.SendTokenAgain.as_view(), name='send_token_again'),
	path('login/<str:user_id>/<str:token>/', views.TokenVerification.as_view(), name='token_verification',),
	path('rest_api/<str:username>/', views.UserData.as_view(), name='userdata'),
]