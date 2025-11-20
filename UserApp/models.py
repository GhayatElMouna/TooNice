from django.db import models

# Create your models here.
             
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import uuid
import random
import string

def validateEmail(value):
    allowed_domains = ['esprit.tn','univ.tn','mit.edu','ox.ac.uk']
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





