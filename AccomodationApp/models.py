from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta

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

    def get_note_moyenne(self):
        """Retourne la note moyenne sur 5 étoiles"""
        notes = self.notes.all()
        if notes.exists():
            moyenne = sum(note.note for note in notes) / notes.count()
            return round(moyenne, 1)
        return None
    
    def get_nombre_avis(self):
        """Retourne le nombre total d'avis"""
        return self.notes.count()
    
    def get_dates_occupees(self):
        """Retourne toutes les dates occupées pour cette accommodation"""
        dates_occupees = set()
        for chambre in self.chambres.all():
            for reservation in chambre.reservations.filter(statut__in=['en_attente', 'confirmee']):
                current_date = reservation.date_debut
                while current_date <= reservation.date_fin:
                    dates_occupees.add(current_date)
                    current_date += timedelta(days=1)
        return sorted(dates_occupees)
    
    def is_disponible(self, date_debut, date_fin):
        """Vérifie si l'accommodation est disponible pour une période donnée"""
        for chambre in self.chambres.all():
            if chambre.is_disponible(date_debut, date_fin):
                return True
        return False

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
    
    def is_disponible(self, date_debut, date_fin):
        """Vérifie si la chambre est disponible pour une période donnée"""
        # Vérifier qu'il n'y a pas de réservation active qui chevauche
        reservations_conflictuelles = self.reservations.filter(
            statut__in=['en_attente', 'confirmee']
        ).filter(
            Q(date_debut__lte=date_fin) & Q(date_fin__gte=date_debut)
        )
        return not reservations_conflictuelles.exists()
    
    def get_dates_occupees(self):
        """Retourne toutes les dates occupées pour cette chambre"""
        dates_occupees = set()
        for reservation in self.reservations.filter(statut__in=['en_attente', 'confirmee']):
            current_date = reservation.date_debut
            while current_date <= reservation.date_fin:
                dates_occupees.add(current_date)
                current_date += timedelta(days=1)
        return sorted(dates_occupees)

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
class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée'),
        ('terminee', 'Terminée'),
    ]
    
    chambre = models.ForeignKey(
        Chambre,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    date_debut = models.DateField(help_text='Date de début de la réservation')
    date_fin = models.DateField(help_text='Date de fin de la réservation')
    nombre_personnes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Nombre de personnes pour cette réservation'
    )
    prix_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Prix total de la réservation'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notes additionnelles pour la réservation'
    )
    
    def __str__(self):
        return f"Réservation {self.chambre.accommodation.titre} - {self.date_debut} au {self.date_fin}"
    
    def is_active(self):
        """Vérifie si la réservation est active (confirmée et non terminée)"""
        return self.statut == 'confirmee' and date.today() <= self.date_fin
    
    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-date_reservation']


class Note(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    note = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Donnez une note de 1 à 5"
    )
    commentaire = models.TextField(max_length=500, blank=True, null=True)
    date_ajoutee = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note {self.note} pour {self.accommodation.titre} par {self.utilisateur.username}"

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        unique_together = [['utilisateur', 'accommodation']]
        ordering = ['-date_ajoutee']

