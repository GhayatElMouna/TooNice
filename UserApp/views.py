from django.shortcuts import render, redirect
from .models import User
from .forms import RegisterForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegisterForm as UserRegisterForm

class RegisterView(CreateView):
    model=User
    form_class=UserRegisterForm
    template_name='UserApp/register.html'
    success_url=reverse_lazy('login')
