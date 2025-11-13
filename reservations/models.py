from django.conf import settings
from django.db import models


class Logement(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    adresse = models.CharField(max_length=255)
    prix_par_nuit = models.DecimalField(max_digits=8, decimal_places=2)
    capacite = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return self.titre


class Reservation(models.Model):
    
    PAIEMENT_CHOICES =[
        ("Card", "Carte bancaire"),
        ("Cash", "Espèces"),
        ("Cheque", "Chèque"),


    ]
    STATUT_CHOICES = [
        ("pending", "En attente"),
        ("confirmed", "Confirmée"),
        ("cancelled", "Annulée"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="reservations", on_delete=models.CASCADE
    )
    logement = models.ForeignKey(Logement, related_name="reservations", on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default="pending")
    mode_paiement = models.CharField(max_length=100, blank=True)
    mode_paiement = models.CharField(
        max_length=20,
        choices=PAIEMENT_CHOICES,
        verbose_name="Mode de paiement",
    )
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self) -> str:
        return f"Réservation #{self.pk} - {self.logement}"

    @property
    def duree_nuits(self):
        if self.date_debut and self.date_fin:
            return (self.date_fin - self.date_debut).days
        return None
