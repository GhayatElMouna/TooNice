from django.shortcuts import render, get_object_or_404
from .models import Event

def event_list(request):
    events = Event.objects.all()
    # template is located at Templates/EventsApp/events.html in this project
    return render(request, 'EventsApp/events.html', {'events': events})

def event_detail(request, id_event):
    event = get_object_or_404(Event, id_event=id_event)
    # use the EventsApp subfolder where templates are stored
    return render(request, 'EventsApp/event_detail.html', {'event': event})
