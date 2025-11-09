from django.db import models
from django.core.validators import MinLengthValidator, FileExtensionValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings  # <-- utiliser AUTH_USER_MODEL

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

    def __str__(self):
        return f"{self.titre} ({self.user.username})"

    def clean(self):
        if len(self.titre.strip()) < 5:
            raise ValidationError("Le titre doit contenir au moins 5 caractères.")

        # Vérifier doublon de titre pour le même utilisateur
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
