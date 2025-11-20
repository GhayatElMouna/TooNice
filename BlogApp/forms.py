from django import forms
from .models import Article
from django.core.exceptions import ValidationError

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        # include chemin_media so users can upload/replace image or video when updating
        fields = ['titre', 'description', 'type_media', 'chemin_media']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'minlength': 5,
                'maxlength': 100,
                'placeholder': 'Titre (min. 5 caractères)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'required': True,
                'minlength': 20,
                'placeholder': 'Décrivez votre article (min. 20 caractères)'
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
            raise ValidationError("Le titre doit contenir au moins 5 caractères.")

        # If we have the user on the instance, prevent duplicate titles for same user
        user = getattr(self.instance, 'user', None)
        if user and Article.objects.filter(titre__iexact=titre, user=user).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Vous avez déjà un article avec ce titre.")

        return titre

    def clean_description(self):
        desc = (self.cleaned_data.get('description') or '').strip()
        if len(desc) < 20:
            raise ValidationError("La description doit contenir au moins 20 caractères.")
        return desc

    def clean_chemin_media(self):
        fichier = self.cleaned_data.get('chemin_media')
        if not fichier:
            return fichier

        # taille
        if hasattr(fichier, 'size') and fichier.size > MAX_UPLOAD_SIZE:
            raise ValidationError("La taille du fichier ne doit pas dépasser 10 MB.")

        # extension
        name = fichier.name.lower()
        if not (name.endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi'))):
            raise ValidationError("Type de fichier non autorisé. Utilisez jpg/png/mp4/mov/avi.")

        # cohérence avec type_media
        type_media = self.cleaned_data.get('type_media') or getattr(self.instance, 'type_media', None)
        if type_media == 'photo' and not name.endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError("Vous avez choisi 'Photo' mais le fichier n'est pas une image.")
        if type_media == 'video' and not name.endswith(('.mp4', '.mov', '.avi')):
            raise ValidationError("Vous avez choisi 'Vidéo' mais le fichier n'est pas une vidéo.")

        return fichier

