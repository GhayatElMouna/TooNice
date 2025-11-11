from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id_user = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_naissance = models.DateField(null=True, blank=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    pays = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'email'  # connexion par email
    REQUIRED_FIELDS = ['username', 'nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom}"


# Create your models here.
