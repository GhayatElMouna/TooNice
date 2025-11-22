from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from EventApp.models import Event
from .models import Participation, Rating
from django.http import JsonResponse


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


"""def my_events(request):
	participations = Participation.objects.filter(user=request.user).select_related('event')
    ############################################
    participations = Participation.objects.filter(
    user=request.user,
    confirmed=False
    ).select_related('event')


    ##########################################
	events = [p.event for p in participations]
	return render(request, 'ParticipationApp/my_events.html', {'events': events})"""
@login_required
def my_events(request):
    participations = Participation.objects.filter(
        user=request.user,
        confirmed=False
    ).select_related('event')

    return render(request, 'ParticipationApp/my_events.html', {'participations': participations})


@login_required
def past_events(request):
    participations = Participation.objects.filter(
        user=request.user,
        confirmed=True
    ).select_related('event')

    events = [p.event for p in participations]

    return render(request, "ParticipationApp/past_events.html", {"events": events})


@login_required
def update_seats(request, participation_id):
    if request.method == "POST":
        participation = get_object_or_404(
            Participation,
            id_participation=participation_id,
            user=request.user
        )
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
    participation = get_object_or_404(
        Participation,
        id_participation=participation_id,
        user=request.user
    )
    event = participation.event

    # Restore seats
    event.capacite += participation.quantity
    event.save()

    participation.delete()

    messages.success(request, "Event removed from your list.")
    return redirect('participation:my_events')

@login_required
def confirm_reservation(request, participation_id):
    participation = get_object_or_404(
        Participation,
        id_participation=participation_id,
        user=request.user
    )

    participation.confirmed = True
    participation.save()

    messages.success(request, "Your reservation has been confirmed.")
    return redirect('participation:my_events')


@login_required
def post_events(request):
    participations = Participation.objects.filter(
        user=request.user,
        confirmed=True
    ).select_related('event')

    return render(request, "ParticipationApp/post_events.html", {"participations": participations})



@login_required

@login_required
def rate_event(request, event_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})

    stars_str = request.POST.get("stars")

    if not stars_str:
        return JsonResponse({"success": False, "error": "No rating value received."})

    try:
        stars = int(stars_str)
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid rating."})

    if stars < 1 or stars > 5:
        return JsonResponse({"success": False, "error": "Rating must be 1 to 5."})

    # Check user finished this event
    participation = Participation.objects.filter(
        user=request.user,
        event_id=event_id,
        confirmed=True
    ).first()

    if not participation:
        return JsonResponse({"success": False, "error": "You cannot rate this event."})

    # Create/update rating
    rating, created = Rating.objects.update_or_create(
        user=request.user,
        event_id=event_id,
        defaults={'stars': stars}
    )

    # Recalculate event average
    event = rating.event
    all_ratings = event.ratings.all()
    avg = sum(r.stars for r in all_ratings) / len(all_ratings)
    event.score_avg = avg
    event.save()

    return JsonResponse({
        "success": True,
        "avg": avg,
        "message": "Rating saved!"
    })
