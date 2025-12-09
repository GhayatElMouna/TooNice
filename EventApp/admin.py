from django.contrib import admin
from .models import Event
import json

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    change_list_template = 'admin/EventApp/event/change_list.html'
    
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

    def changelist_view(self, request, extra_context=None):
        # Calculate statistics for the chart
        events = Event.objects.all()
        
        # Count how many events have each score
        score_count = {}
        for e in events:
            score = round(e.score_avg or 0, 1)  # Round to 1 decimal like 3.5
            score_count[score] = score_count.get(score, 0) + 1

        total = sum(score_count.values()) if score_count else 1  # Avoid division by zero

        # Convert counts → percentages
        percentages = {
            score: round((count / total) * 100, 2)
            for score, count in score_count.items()
        }

        labels = [str(score) for score in percentages.keys()]
        scores = list(percentages.values())

        # Add chart data to context
        extra_context = extra_context or {}
        extra_context['chart_labels'] = json.dumps(labels)
        extra_context['chart_scores'] = json.dumps(scores)
        
        return super().changelist_view(request, extra_context=extra_context)
