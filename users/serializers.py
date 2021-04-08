from rest_framework import serializers
from .models import User

class UserDataSerializer(serializers.ModelSerializer):
	
	"""
	Модель для сериализации данных пользователя, предназначенная
	для представления данных функцией REST API Simple User Data
	"""
	
	class Meta:
		model = User
		fields = ('username', 'email',)