from django import forms
from .models import Article
from django.core.exceptions import ValidationError

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'description', 'type_media', 'chemin_media']
        labels = {
            'titre': 'Title',
            'description': 'Description',
            'type_media': 'Media Type',
            'chemin_media': 'Media File',
        }
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'minlength': 5,
                'maxlength': 100,
                'placeholder': 'Title (min. 5 characters)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'required': True,
                'minlength': 20,
                'placeholder': 'Describe your article (min. 20 characters)'
            }),
            'type_media': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'chemin_media': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*'
            })
        }

    def clean_titre(self):
        titre = (self.cleaned_data.get('titre') or '').strip()
        if len(titre) < 5:
            raise ValidationError("Title must be at least 5 characters long.")

        user = getattr(self.instance, 'user', None)
        if user and Article.objects.filter(titre__iexact=titre, user=user).exclude(pk=self.instance.pk).exists():
            raise ValidationError("You already have an article with this title.")

        return titre

    def clean_description(self):
        desc = (self.cleaned_data.get('description') or '').strip()
        if len(desc) < 20:
            raise ValidationError("Description must be at least 20 characters long.")
        return desc

    def clean_chemin_media(self):
        fichier = self.cleaned_data.get('chemin_media')
        if not fichier:
            return fichier

        if hasattr(fichier, 'size') and fichier.size > MAX_UPLOAD_SIZE:
            raise ValidationError("File size must not exceed 10 MB.")

        name = fichier.name.lower()
        if not (name.endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi'))):
            raise ValidationError("Invalid file type. Use jpg/png/mp4/mov/avi.")

        type_media = self.cleaned_data.get('type_media') or getattr(self.instance, 'type_media', None)
        if type_media == 'photo' and not name.endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError("You selected 'Photo' but the file is not an image.")
        if type_media == 'video' and not name.endswith(('.mp4', '.mov', '.avi')):
            raise ValidationError("You selected 'Video' but the file is not a video.")

        return fichier
