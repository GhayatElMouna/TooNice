from django.db import models
from django.core.validators import MinLengthValidator, FileExtensionValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

# Validators
titre_validator = RegexValidator(
    regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\_\'"]+$',
    message="Le titre ne doit contenir que des lettres, chiffres, espaces ou tirets."
)

description_validator = MinLengthValidator(
    20, "La description doit contenir au moins 20 caractères."
)

media_validator = FileExtensionValidator(
    allowed_extensions=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'],
    message="Le fichier doit être une image (.jpg, .png) ou une vidéo (.mp4, .mov, .avi)."
)

class Article(models.Model):
    MEDIA_CHOICES = [
        ("photo", "Photo"),
        ("video", "Vidéo"),
    ]

    id_article = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=100, validators=[titre_validator])
    description = models.TextField(validators=[description_validator])
    type_media = models.CharField(max_length=10, choices=MEDIA_CHOICES)
    chemin_media = models.FileField(upload_to="uploads/", validators=[media_validator])
    date_publication = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Statistiques
    nb_likes = models.PositiveIntegerField(default=0)
    nb_dislikes = models.PositiveIntegerField(default=0)
    nb_vues = models.PositiveIntegerField(default=0)
    nb_infractions = models.PositiveIntegerField(default=0)
    statut = models.CharField(max_length=50, default="en_attente")
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_articles', blank=True)
    disliked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_articles', blank=True)
    # Stocke une liste ordonnée de recommandations pré-calculées: [{'id': <pk>, 'score': 0.87}, ...]
    recommendations = models.JSONField(default=list, blank=True)

    def __str__(self):
        user_str = self.user.username if self.user_id else "Utilisateur non assigné"
        return f"{self.titre} ({user_str})"

    def clean(self):
        if len(self.titre.strip()) < 5:
            raise ValidationError("Le titre doit contenir au moins 5 caractères.")

        # ⚠ Vérifie que l'utilisateur est assigné avant d’accéder à self.user
        if self.user_id:  # user_id est None si non assigné
            if Article.objects.filter(
                titre__iexact=self.titre.strip(),
                user=self.user
            ).exclude(pk=self.pk).exists():
                raise ValidationError("Vous avez déjà un article avec ce titre.")

        # Vérifier cohérence type_media / chemin_media
        if self.type_media == "photo" and not self.chemin_media.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError("Le fichier doit être une image (.jpg, .jpeg ou .png).")
        elif self.type_media == "video" and not self.chemin_media.name.lower().endswith(('.mp4', '.mov', '.avi')):
            raise ValidationError("Le fichier doit être une vidéo (.mp4, .mov ou .avi).")
