from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

# Create your views here.

#Home page
def home(request):
	return render(request, 'home.html')

# Class Based CreateView for customer registeration
class register_customer(SuccessMessageMixin, CreateView):
	success_url = reverse_lazy('admin:login')
	success_message = 'Registration successfull!.'
	form_class = NewCustomerForm
	template_name = 'customer/register.html'