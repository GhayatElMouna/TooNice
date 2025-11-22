from django.db import models
from django.conf import settings
from django.utils import timezone
from EventApp.models import Event




class Participation(models.Model):
    id_participation = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    event = models.ForeignKey(
        'EventApp.Event',
        on_delete=models.CASCADE,
        related_name='participants'
    )
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)#best practise a rechercher
	
    quantity = models.PositiveIntegerField(default=1)
    confirmed = models.BooleanField(default=False)


    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} → {self.event.title}"

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveIntegerField(default=0)  # value from 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')  # a user can rate an event only once

    def __str__(self):
        return f"{self.user} - {self.event.title} : {self.stars} stars"

