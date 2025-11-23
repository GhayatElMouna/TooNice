from django.db import models

# Create your models here.
             
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import uuid
import random
import string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta



def validateEmail(value):
    allowed_domains = ['gmail.com','esprit.tn','univ.tn','mit.edu','ox.ac.uk']
    domain = value.split('@')[-1]
    if domain not in allowed_domains:
        raise ValidationError(f"Email domain '{domain}' is not allowed. Allowed domains are: {', '.join(allowed_domains)}") 



def generate_user_id():
    # Génère un identifiant unique du type userXXXXXX (6 caractères alphanumériques)
    return "user" + uuid.uuid4().hex[:4].upper()

name_validator= RegexValidator(
    regex=r'^[a-zA-Z\s]+$',
    message="This field should contain only alphabetic characters."
)


# Create your models here.
class User(AbstractUser):
    user_id = models.CharField(max_length=8, primary_key=True, unique=True, editable=False)    
    first_name=models.CharField(max_length=30,validators=[name_validator])
    last_name=models.CharField(max_length=30,validators=[name_validator])
    email=models.EmailField(unique=True, validators=[validateEmail])
    infractions = models.IntegerField(default=0)
    blocked_until = models.DateTimeField(null=True, blank=True)
    # created_at=models.DateTimeField(auto_now_add=True)
    # updated_at=models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user_id:
            new_id = generate_user_id()

            while User.objects.filter(user_id=new_id).exists():
                new_id = generate_user_id()
            self.user_id = new_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username



class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # ⚡ Champs pour gestion des posts inappropriés
    bad_post_attempts = models.PositiveIntegerField(default=0)
    blocked_until = models.DateTimeField(null=True, blank=True)

    def is_blocked(self):
        return self.blocked_until and timezone.now() < self.blocked_until

    def block_for_two_days(self):
        self.blocked_until = timezone.now() + timedelta(days=2)
        self.save()

    def __str__(self):
        return f"{self.user.username} Profile"
