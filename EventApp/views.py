from django.shortcuts import render, get_object_or_404
from .models import Event
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg
from ParticipationApp.models import Rating
from collections import Counter



def event_list(request):
    events = Event.objects.all()

    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')
    state = request.GET.get('state')

    if start_date and end_date:
        events = events.filter(date_debut__range=[start_date, end_date])

    if category:
        events = events.filter(category=category)

    if state:
        events = events.filter(place__icontains=state)  # assuming 'place' stores the city/governorate

    context = {
        'events': events,
        'start_date': start_date,
        'end_date': end_date,
        'category': category,
        'state': state,
    }
    return render(request, 'EventsApp/events.html', context)

def event_detail(request, id_event):
    event = get_object_or_404(Event, id_event=id_event)
    # use the EventsApp subfolder where templates are stored
    return render(request, 'EventsApp/event_detail.html', {'event': event})


@staff_member_required
def event_stats(request):
     # Get all event scores (already calculated)
    events = Event.objects.all()

    # Count how many events have each score
    score_count = {}
    for e in events:
        score = round(e.score_avg or 0, 1)  # Round to 1 decimal like 3.5
        score_count[score] = score_count.get(score, 0) + 1

    total = sum(score_count.values())  # Total number of events

    # Convert counts → percentages
    percentages = {
        score: round((count / total) * 100, 2)
        for score, count in score_count.items()
    }

    labels = list(percentages.keys())
    scores = list(percentages.values())

    return render(request, "EventsApp/event_stats.html", {
        "labels": labels,
        "scores": scores,
    })