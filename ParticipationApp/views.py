from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from EventApp.models import Event
from .models import Participation, Rating
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import localdate
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import qrcode


@login_required
def register_event(request, event_id):
    # Only accept POST for registration
    if request.method != 'POST':
        return redirect('event_list')

    event = get_object_or_404(Event, id_event=event_id)

    # Check if capacity is available
    if event.capacite <= 0:
        messages.error(request, 'This event is fully booked.')
        return redirect('participation:my_events')

    # Prevent duplicate registrations
    already = Participation.objects.filter(user=request.user, event=event).exists()
    if already:
        messages.info(request, 'You have already registered for this event.')
        return redirect('participation:my_events')

    # Create participation and decrement capacity atomically
    # Simple approach: update and save (for heavy concurrency use DB transactions)
    Participation.objects.create(user=request.user, event=event)
    event.capacite = max(0, event.capacite - 1)
    event.save()
    messages.success(request, 'Successfully registered for the event.')
    return redirect('participation:my_events')


"""@login_required
def my_events(request):
    participations = Participation.objects.filter(
        user=request.user,
        confirmed=False
    ).select_related('event')

    return render(request, 'ParticipationApp/my_events.html', {'participations': participations})"""

@login_required
def my_events(request):
    # Show only unconfirmed ("cart") participations
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

def generate_ticket_pdf(participation):
    """Generate a PDF ticket for the event participation - concert ticket style"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from PIL import Image as PILImage
    from colorthief import ColorThief
    from django.conf import settings
    import os
    
    # Register custom fonts
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    blacksword_path = os.path.join(font_dir, 'Blacksword.otf')
    birds_path = os.path.join(font_dir, 'Birds of Paradise © PERSONAL USE ONLY.ttf')
    
    try:
        pdfmetrics.registerFont(TTFont('Blacksword', blacksword_path))
    except:
        pass
    try:
        pdfmetrics.registerFont(TTFont('BirdsOfParadise', birds_path))
    except:
        pass
    
    buffer = BytesIO()

    # Ticket dimensions (landscape rectangle like a concert ticket)
    ticket_width = 8 * inch
    ticket_height = 3.5 * inch

    c = canvas.Canvas(buffer, pagesize=(ticket_width, ticket_height))

    event = participation.event
    user = participation.user

    # Build a color palette that matches the event image
    def _make_color(rgb_tuple, default_hex):
        if not rgb_tuple:
            return colors.HexColor(default_hex)
        return colors.Color(rgb_tuple[0]/255, rgb_tuple[1]/255, rgb_tuple[2]/255)

    primary = colors.HexColor('#f5f5f5')
    secondary = colors.HexColor('#e8e8e8')
    accent = colors.HexColor('#d0d0d0')
    try:
        if event.image and os.path.exists(event.image.path):
            ct = ColorThief(event.image.path)
            palette = ct.get_palette(color_count=4, quality=1)
            primary = _make_color(palette[0], '#f5f5f5')
            secondary = _make_color(palette[1] if len(palette) > 1 else None, '#e8e8e8')
            accent = _make_color(palette[2] if len(palette) > 2 else None, '#d0d0d0')
    except Exception:
        # keep defaults on failure
        pass

    # Compute title color: lighten if background is dark, darken if background is light
    def _adjust_title_color(base_color):
        r, g, b = base_color.red, base_color.green, base_color.blue
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        if luminance < 0.5:
            # lighten by blending toward white
            factor = 0.55
            return colors.Color(r + (1 - r) * factor, g + (1 - g) * factor, b + (1 - b) * factor)
        else:
            # darken by blending toward black
            factor = 0.55
            return colors.Color(r * (1 - factor), g * (1 - factor), b * (1 - factor))

    title_color = _adjust_title_color(primary)

    # Background blocks using palette (no transparency to avoid artifacts)
    c.setFillColor(primary)
    c.rect(0, 0, ticket_width, ticket_height, fill=True, stroke=False)
    c.setFillColor(secondary)
    c.rect(0, 0, ticket_width * 0.62, ticket_height, fill=True, stroke=False)
    c.setFillColor(accent)
    c.rect(ticket_width * 0.62, 0, ticket_width * 0.1, ticket_height, fill=True, stroke=False)
    
    # Add event image (right side)
    if event.image and os.path.exists(event.image.path):
        try:
            img_x = ticket_width - 2.8*inch
            img_y = 0.3*inch
            img_width = 2.5*inch
            img_height = ticket_height - 0.6*inch
            
            c.drawImage(event.image.path, img_x, img_y, 
                       width=img_width, height=img_height, 
                       preserveAspectRatio=True)
        except:
            pass
    
    # Left side content
    left_margin = 0.3*inch
    
    # Event title (higher placement, stylized font)
    c.setFillColor(title_color)
    try:
        c.setFont("BirdsOfParadise", 32)
    except:
        try:
            c.setFont("Blacksword", 30)
        except:
            c.setFont("Helvetica-Bold", 24)
    title_y = ticket_height - 0.75*inch
    
    # Wrap title if too long
    title = event.title
    if len(title) > 30:
        title = title[:30] + "..."
    c.drawString(left_margin, title_y, title)
    
    # Event details (shifted up)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    details_y = title_y - 0.4*inch
    
    c.drawString(left_margin, details_y, "Location")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    c.drawString(left_margin + 0.1*inch, details_y - 0.2*inch, event.place[:40])
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(left_margin, details_y - 0.55*inch, "DATE")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    date_str = event.date_debut.strftime("%d %B %Y")
    if event.date_fin and event.date_fin != event.date_debut:
        date_str += f" - {event.date_fin.strftime('%d %b %Y')}"
    c.drawString(left_margin + 0.1*inch, details_y - 0.75*inch, date_str)
    
    # Number of seats
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(left_margin + 2.5*inch, details_y, "SEATS")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    c.drawString(left_margin + 2.6*inch, details_y - 0.2*inch, str(participation.quantity))
    
    # Price (DT instead of $)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(left_margin + 2.5*inch, details_y - 0.55*inch, "PRICE")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    price_text = f"{event.ticket_price} DT" if event.ticket_price else "FREE"
    c.drawString(left_margin + 2.6*inch, details_y - 0.75*inch, price_text)
    
    # Decorative elements
    c.setStrokeColor(colors.HexColor('#cccccc'))
    c.setLineWidth(1)
    c.line(ticket_width - 3*inch, 0.1*inch, ticket_width - 3*inch, ticket_height - 0.1*inch)
    
    # Finalize
    c.save()
    buffer.seek(0)
    return buffer


@login_required
def confirm_reservation(request, participation_id):
    participation = get_object_or_404(
        Participation,
        id_participation=participation_id,
        user=request.user
    )

    participation.confirmed = True
    participation.save()

    # Generate and return the PDF ticket
    pdf_buffer = generate_ticket_pdf(participation)
    
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{participation.event.title.replace(" ", "_")}_{participation.id_participation}.pdf"'
    
    messages.success(request, "Your reservation has been confirmed and your ticket has been downloaded.")
    
    # After PDF is returned, we'll use JavaScript redirect or just return the PDF
    # Since we can't redirect after sending file, we'll store session and show message
    return response



@login_required
def post_events(request):
    participations = Participation.objects.filter(
        user=request.user,
        confirmed=True
    ).select_related('event')

    # Add is_finished flag to each event
    today = localdate()
    for p in participations:
        
        p.event.is_finished = p.event.date_fin <= today
        p.event.stars_display = round(p.event.score_avg)  # arrondi à l'entier le plus proche


    return render(request, "ParticipationApp/post_events.html", {"participations": participations})





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

    participation = Participation.objects.filter(
        user=request.user,
        event_id=event_id,
        confirmed=True
    ).first()

    if not participation:
        return JsonResponse({"success": False, "error": "You cannot rate this event."})

    # Check if the event is finished
    event = participation.event
    if event.date_fin > localdate():
        return JsonResponse({"success": False, "error": "Vous ne pouvez pas noter un événement non terminé."})

    # Create/update rating
    rating, created = Rating.objects.update_or_create(
        user=request.user,
        event_id=event_id,
        defaults={'stars': stars}
    )

    # Recalculate average
    all_ratings = event.ratings.all()
    avg = sum(r.stars for r in all_ratings) / len(all_ratings)
    event.score_avg = avg
    event.save()

    return JsonResponse({
        "success": True,
        "avg": avg,
        "message": "Rating saved!"
    })

