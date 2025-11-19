from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from datetime import date

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('CULTURAL', 'Cultural & Historical'),
        ('MUSIC', 'Music & Arts'),
        ('SEASONAL', 'Seasonal & Agricultural'),
        ('SPORT', 'Sporting Events'),
        ('CRAFT', 'Craftsmanship & Shopping'),
    ]

    id_event = models.AutoField(primary_key=True)  # auto-incremented ID
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    place = models.CharField(max_length=200)
    capacite = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    score_avg = models.FloatField(default=0.0)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.ImageField(
        upload_to='event_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        # Ensure the start date is not in the past (must be today or later)
        if self.date_debut:
            if self.date_debut < date.today():
                raise ValidationError({
                    'date_debut': _('Start date cannot be in the past.'),
                })

        # Ensure start is not after end
        if self.date_debut and self.date_fin:
            if self.date_debut > self.date_fin:
                raise ValidationError({
                    'date_debut': _('Start date cannot be later than end date.'),
                    'date_fin': _('End date cannot be earlier than start date.')
                })

    def __str__(self):
        return f"{self.title} ({self.category})"

    class Meta:
        ordering = ['-date_debut']
