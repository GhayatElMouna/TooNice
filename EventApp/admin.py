from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_debut', 'date_fin', 'place', 'capacite', 'ticket_price', 'score_avg', 'image_preview')
    list_filter = ('category', 'date_debut', 'place')
    search_fields = ('title', 'place', 'description')
    ordering = ('-date_debut',)
    readonly_fields = ('score_avg', 'image_preview')

    # Optional: show a small image preview in the admin
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="60" />'
        return "-"
    image_preview.allow_tags = True
    image_preview.short_description = 'Image'
