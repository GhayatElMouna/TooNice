"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    affiliation = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre affiliation'}))
    nationality = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nationalité'}))

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'role', 'affiliation', 'nationality']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez'}),
        }
        labels = {
            'email': 'Email (utilisé pour login)',
            'username': 'Nom d\'utilisateur',
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'role': 'Rôle',
            'affiliation': 'Affiliation',
            'nationality': 'Nationalité',
        }
        """
# UserApp/forms.py
from django import forms
from django.contrib.auth import authenticate
from .models import User

class SignInForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise forms.ValidationError("Email ou mot de passe incorrect")
        self.cleaned_data['user'] = user
        return self.cleaned_data
    # UserApp/forms.py
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data["password"])
        
        # SÉCURITÉ : UTILISATEUR NORMAL
        user.is_staff = False      # PAS d'accès admin
        user.is_superuser = False  # PAS de superpouvoirs
        
        if commit:
            user.save()
        return user


from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class SignUpForm(forms.ModelForm):
    # ON GARDE LES NOMS DE TON HTML
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        min_length=8
    )
    confirmPassword = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'})
    )

    class Meta:
        model = User
        fields = ['email', 'nom', 'prenom', 'date_naissance', 'pays', 'adresse']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'pays': forms.TextInput(attrs={'placeholder': 'Entrez votre pays'}),
            'adresse': forms.TextInput(attrs={'placeholder': 'Entrez votre adresse'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmPassword = cleaned_data.get("confirmPassword")
        if password and confirmPassword and password != confirmPassword:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    # UserApp/forms.py
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data["password"])
        
        # SÉCURITÉ : UTILISATEUR NORMAL
        user.is_staff = False      # PAS d'accès admin
        user.is_superuser = False  # PAS de superpouvoirs
        
        if commit:
            user.save()
        return user