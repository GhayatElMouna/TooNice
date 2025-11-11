# UserApp/views.py
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import SignInForm
from .forms import SignUpForm
from django.views.generic.edit import CreateView

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.views.generic.edit import UpdateView
from .models import User




class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
    login_url = 'user_signin'  # Redirige si pas connecté

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['prenom', 'nom', 'email', 'date_naissance', 'pays', 'adresse']
    success_url = reverse_lazy('profile')
    login_url = 'user_signin'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil mis à jour avec succès !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erreur dans le formulaire.")
        return HttpResponseRedirect(reverse_lazy('profile'))

    # CRUCIAL : Autorise POST
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class IndexAuthView(LoginRequiredMixin, TemplateView):
    template_name = 'index_auth.html'
    login_url = 'user_signin'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('user_signin')  # ← reverse_lazy (pas string)

class IndexView(TemplateView):
    template_name = 'index.html'

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('user_signin')

    def form_valid(self, form):
        user = form.save()  # form.save() appelle la méthode save() ci-dessus
        login(self.request, user)
        messages.success(self.request, f"Compte créé avec succès, {user.prenom} !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Veuillez corriger les erreurs.")
        return super().form_invalid(form)

class SignInView(FormView):
    template_name = 'signin.html'  # ← CORRECT : templates/ à la racine
    form_class = SignInForm
    success_url = reverse_lazy('index_auth')  # ou 'user_signin' si tu veux boucle

    def form_valid(self, form):
        user = form.cleaned_data['user']
        login(self.request, user)
        messages.success(self.request, f"Welcome back, {user.nom}!")
        return super().form_valid(form)