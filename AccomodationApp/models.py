from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, FileExtensionValidator
from django.utils import timezone
from datetime import date
class Accommodation(models.Model):
    # --- Validator pour le titre (lettres, chiffres, espaces)
    titre_validator = RegexValidator(
        regex=r'^[\w\s]+$',
        message='Le titre ne doit contenir que des lettres, chiffres et espaces.'
    )

    TYPE_CHOICES = [
        ("maison_dhote", "Maison d'hôte"),
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

    # --- Champs du modèle
    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=200, validators=[titre_validator])
    description = models.TextField(max_length=500, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    gouvernorat = models.CharField(max_length=50, choices=GOUVERNORAT_CHOICES)
    prix = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(0.01)], help_text="Prix minimum peut être surchargé par les chambres")
    adresse = models.CharField(max_length=255, blank=True, null=True)
    date_ajoutee = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True, help_text="Le logement est-il actuellement disponible à la location ?")

    # --- Relation ManyToMany avec les utilisateurs
    utilisateurs = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="accommodations")

    def __str__(self):
        return f"{self.titre} ({self.get_gouvernorat_display()})"

    def get_nombre_chambres(self):
        """Retourne le nombre total de chambres pour cette accommodation"""
        return self.chambres.count()

   


    class Meta:
        verbose_name = "Hébergement"
        verbose_name_plural = "Hébergements"
        ordering = ['-date_ajoutee']


class Chambre(models.Model):
    TYPE_CHOICES = [
        ('simple', 'Chambre Simple'),
        ('double', 'Chambre Double'),
        ('twin', 'Chambre Twin'),
        ('triple', 'Chambre Triple'),
        ('suite', 'Suite'),
        ('familiale', 'Chambre Familiale'),
        ('dortoir', 'Dortoir'),
    ]

    # --- Relation avec Accommodation
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='chambres')
    
    # --- Informations de la chambre
    numero = models.CharField(max_length=50, help_text='Numéro ou nom de la chambre')
    type_chambre = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(max_length=500, null=True)
    
    # --- Capacité et lits
    nombre_lits = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Nombre de lits dans la chambre'
    )
  
    
    # --- Prix et disponibilité
    prix_nuit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Prix par nuit pour cette chambre'
    )
  
    
    # --- Date d'ajout
    date_ajoutee = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.numero} - {self.accommodation.titre}"


    class Meta:
        verbose_name = "Chambre"
        verbose_name_plural = "Chambres"
        unique_together = [['accommodation', 'numero']]
        ordering = ['accommodation', 'numero']


class Photo(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(
        upload_to="accommodations/photos/",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    
    def __str__(self):
        return f"Photo de {self.accommodation.titre}"

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"


