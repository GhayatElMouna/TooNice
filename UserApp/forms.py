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