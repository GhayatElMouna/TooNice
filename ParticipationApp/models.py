from django.db import models
from django.conf import settings
from django.utils import timezone


# Participation model: link a user to an event they registered for
class Participation(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations')
	event = models.ForeignKey('EventApp.Event', on_delete=models.CASCADE, related_name='participants')
	created_at = models.DateTimeField(default=timezone.now)
	quantity = models.PositiveIntegerField(default=1)

	class Meta:
		unique_together = ('user', 'event')

	def __str__(self):
		return f"{self.user} -> {self.event}"
