""""
from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display=("user_id","username","first_name","last_name","email","role")
    search_fields=("user_id","username","email")
# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.site_header="User Managment Dadhboard"
admin.site.site_title="User"
admin.site.index_title="Dashboard"
"""
# UserApp/admin.py
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'nom', 'prenom', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'nom', 'prenom')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')

    fieldsets = (
        ('Informations', {
            'fields': ('email', 'password')
        }),
        ('Détails personnels', {
            'fields': ('nom', 'prenom', 'date_naissance', 'pays', 'adresse')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Pour hacher le mot de passe lors de la création
    def save_model(self, request, obj, form, change):
        if not change:  # Création
            obj.set_password(form.cleaned_data['password'])
        else:
            # Si mot de passe modifié
            if 'password' in form.changed_data:
                obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


