from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from EventApp.models import Event
from .models import Participation


@login_required
def register_event(request, event_id):
	# Only accept POST for registration
	if request.method != 'POST':
		return redirect('event_list')

	event = get_object_or_404(Event, id_event=event_id)

	# Check if capacity is available
	if event.capacite <= 0:
		messages.error(request, 'This event is fully booked.')
		return redirect('event_list')

	# Prevent duplicate registrations
	already = Participation.objects.filter(user=request.user, event=event).exists()
	if already:
		messages.info(request, 'You have already registered for this event.')
		return redirect('event_list')

	# Create participation and decrement capacity atomically
	# Simple approach: update and save (for heavy concurrency use DB transactions)
	Participation.objects.create(user=request.user, event=event)
	event.capacite = max(0, event.capacite - 1)
	event.save()
	messages.success(request, 'Successfully registered for the event.')
	return redirect('event_list')


@login_required
def my_events(request):
	participations = Participation.objects.filter(user=request.user).select_related('event')
	events = [p.event for p in participations]
	return render(request, 'ParticipationApp/my_events.html', {'events': events})

@login_required
def update_seats(request, participation_id):
    if request.method == "POST":
        participation = get_object_or_404(Participation, id=participation_id, user=request.user)
        event = participation.event

        new_qty = int(request.POST.get("quantity"))
        old_qty = participation.quantity

        if new_qty < 1:
            messages.error(request, "Quantity must be at least 1.")
            return redirect('participation:my_events')

        # Calculate difference
        diff = new_qty - old_qty

        # If adding seats, check capacity
        if diff > 0 and event.capacite < diff:
            messages.error(request, "Not enough seats available.")
            return redirect('participation:my_events')

        # Update event capacity
        event.capacite -= diff
        event.save()

        # Update participation
        participation.quantity = new_qty
        participation.save()

        messages.success(request, "Seats updated successfully.")
        return redirect('participation:my_events')

    return redirect('participation:my_events')


@login_required
def delete_participation(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id, user=request.user)
    event = participation.event

    # Restore seats
    event.capacite += participation.quantity
    event.save()

    participation.delete()

    messages.success(request, "Event removed from your list.")
    return redirect('participation:my_events')