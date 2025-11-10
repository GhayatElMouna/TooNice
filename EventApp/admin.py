from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_debut', 'date_fin', 'place', 'capacite', 'ticket_price', 'score_avg')
    list_filter = ('category', 'date_debut', 'place')
    search_fields = ('title', 'place', 'description')
    ordering = ('-date_debut',)
    readonly_fields = ('score_avg',)
