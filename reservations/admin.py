from django.contrib import admin
from .models import Logement, Reservation


@admin.register(Logement)
class LogementAdmin(admin.ModelAdmin):
    list_display = ("titre", "adresse", "prix_par_nuit", "capacite")
    search_fields = ("titre", "adresse")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "logement", "date_debut", "date_fin", "statut", "prix_total")
    list_filter = ("statut", "date_debut")
    search_fields = ("user__username", "logement__titre")
