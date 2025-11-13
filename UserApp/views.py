from django.shortcuts import render, redirect
from .models import User
from .forms import RegisterForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from .forms import RegisterForm as UserRegisterForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class RegisterView(CreateView):
    model=User
    form_class=UserRegisterForm
    template_name='UserApp/register.html'
    # after registering, redirect to the site homepage
    success_url=reverse_lazy('index')

    def form_valid(self, form):
        # Save the new user first
        response = super().form_valid(form)
        # Authenticate and log the user in immediately
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
        return response


class AdminAwareLoginView(LoginView):
    """LoginView that redirects superusers to the Django admin dashboard by default.

    Behavior:
    - If a 'next' parameter is present, honor it.
    - If the authenticated user is a superuser, redirect to 'admin:index'.
    - Otherwise fall back to the normal LOGIN_REDIRECT_URL.
    """

    def get_success_url(self):
        # If a 'next' parameter was supplied, keep it
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to

        # If the logged-in user is a superuser, send them to admin dashboard
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return reverse_lazy('admin:index')

        # Fallback to default behavior
        return super().get_success_url()
