from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('register/', register_customer.as_view(), name="register"),
	path('', home, name="home"),
	path('password_reset/', auth_views.PasswordResetView.as_view(success_url='done/', html_email_template_name='registration/password_reset_email.html'), name="password_reset"),
	path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
	path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url='/reset/done/', post_reset_login=True), name="password_reset_confirm"),
	path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]