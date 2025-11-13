from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'description', 'type_media']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type_media': forms.Select(attrs={'class': 'form-select'}),
            'chemin_media': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

