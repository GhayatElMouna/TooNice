from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, RegexValidator

class Accommodation(models.Model):
    # --- Validator pour le titre (lettres, chiffres, espaces)
    titre_validator = RegexValidator(
        regex=r'^[\w\s]+$',
        message='Le titre ne doit contenir que des lettres, chiffres et espaces.'
    )

    TYPE_CHOICES = [
        ("maison_dhote", "Maison d’hôte"),
        ("gite_rural", "Gîte rural"),
        ("camping_tente", "Camping / Tente"),
        ("hotel", "Hôtel"),
        ("riad", "Riad / Dar"),
        ("autre", "Autre"),
    ]

    GOUVERNORAT_CHOICES = [
        ("tunis", "Tunis"),
        ("ariana", "Ariana"),
        ("ben_arous", "Ben Arous"),
        ("manouba", "Manouba"),
        ("nabeul", "Nabeul"),
        ("zaghouan", "Zaghouan"),
        ("bizerte", "Bizerte"),
        ("beja", "Béja"),
        ("jendouba", "Jendouba"),
        ("kef", "Le Kef"),
        ("siliana", "Siliana"),
        ("sousse", "Sousse"),
        ("monastir", "Monastir"),
        ("mahdia", "Mahdia"),
        ("sfax", "Sfax"),
        ("kairouan", "Kairouan"),
        ("kasserine", "Kasserine"),
        ("sidi_bouzid", "Sidi Bouzid"),
        ("gabes", "Gabès"),
        ("medenine", "Medenine"),
        ("tataouine", "Tataouine"),
        ("tozeur", "Tozeur"),
        ("kebili", "Kébili"),
        ("gafsa", "Gafsa"),
    ]

    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=200, validators=[titre_validator])
    description = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    gouvernorat = models.CharField(max_length=50, choices=GOUVERNORAT_CHOICES)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    date_ajoutee = models.DateTimeField(auto_now_add=True)

    utilisateurs = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="accommodations")

    def __str__(self):
        return f"{self.titre} ({self.get_gouvernorat_display()})"

class Photo(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(
        upload_to="accommodations/photos/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])]
    )
    
    def __str__(self):
        return f"Photo de {self.accommodation.titre}"
