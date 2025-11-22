from django.shortcuts import render, get_object_or_404
from .models import Event

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
