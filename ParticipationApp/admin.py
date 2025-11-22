from django.contrib import admin
from .models import Participation

@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'quantity', 'created_at')
    list_filter = ('created_at', 'event')
    search_fields = ('user__username', 'event__title')
    ordering = ('-created_at',)
