from django.urls import path, include
from .views import *

urlpatterns = [
	path('register/', register_customer.as_view(), name="register"),
	path('', home, name="home"),
]