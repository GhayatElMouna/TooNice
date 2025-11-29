from django.contrib import admin
from django import forms
from .models import Accommodation, Photo, Chambre, Note, Reservation

# --- Inlines ---

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

class ChambreInline(admin.TabularInline):
    model = Chambre
    extra = 1
    fields = ('numero', 'type_chambre', 'nombre_lits', 'prix_nuit')
    show_change_link = True

# --- Admin Accommodation ---

@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type', 'gouvernorat', 'prix', 'est_actif', 'nombre_chambres_display', 'date_ajoutee')
    list_filter = ('type', 'gouvernorat', 'est_actif', 'date_ajoutee')
    search_fields = ('titre', 'description', 'adresse')
    readonly_fields = ('date_ajoutee',)
    filter_horizontal = ('utilisateurs',)  # cache ce champ du formulaire
    inlines = [ChambreInline, PhotoInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'type', 'gouvernorat', 'adresse', 'prix', 'est_actif')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """Cache le champ utilisateurs mais le garde fonctionnel"""
        form = super().get_form(request, obj, **kwargs)
        if 'utilisateurs' in form.base_fields:
            form.base_fields['utilisateurs'].widget = forms.MultipleHiddenInput()
        return form

    def nombre_chambres_display(self, obj):
        """Affiche le nombre de chambres"""
        return obj.get_nombre_chambres()
    nombre_chambres_display.short_description = 'Nombre de chambres'

# --- Admin Chambre ---

@admin.register(Chambre)
class ChambreAdmin(admin.ModelAdmin):
    list_display = ('numero', 'accommodation', 'type_chambre', 'nombre_lits', 'prix_nuit', 'date_ajoutee')
    list_filter = ('type_chambre', 'accommodation', 'date_ajoutee')
    search_fields = ('numero', 'accommodation__titre', 'description')
    readonly_fields = ('date_ajoutee',)
    fieldsets = (
        ('Informations de la chambre', {
            'fields': ('accommodation', 'numero', 'type_chambre', 'description')
        }),
        ('Capacité et prix', {
            'fields': ('nombre_lits', 'prix_nuit')
        }),
    )

# --- Admin Photo ---

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'accommodation', 'image')
    list_filter = ('accommodation',)
    search_fields = ('accommodation__titre',)

# --- Admin Note ---

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('chambre', 'utilisateur', 'date_debut', 'date_fin', 'statut', 'prix_total', 'date_reservation')
    list_filter = ('statut', 'date_debut', 'date_fin', 'date_reservation')
    search_fields = ('chambre__accommodation__titre', 'chambre__numero', 'utilisateur__username')
    readonly_fields = ('date_reservation', 'date_modification')
    date_hierarchy = 'date_debut'
    
    fieldsets = (
        ('Informations de réservation', {
            'fields': ('chambre', 'utilisateur', 'date_debut', 'date_fin', 'nombre_personnes')
        }),
        ('Détails financiers', {
            'fields': ('prix_total',)
        }),
        ('Statut', {
            'fields': ('statut', 'notes')
        }),
        ('Dates', {
            'fields': ('date_reservation', 'date_modification')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Remplit automatiquement l'utilisateur connecté si vide"""
        if not obj.utilisateur_id:  # Si pas d'utilisateur sélectionné
            obj.utilisateur = request.user
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        """Pré-remplit l'utilisateur avec l'utilisateur connecté lors de la création"""
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Si c'est une nouvelle réservation
            # Pré-remplir avec l'utilisateur connecté
            form.base_fields['utilisateur'].initial = request.user
            # Rendre le champ optionnel dans le formulaire (mais il sera rempli automatiquement)
            form.base_fields['utilisateur'].required = False
        return form

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'utilisateur', 'note', 'date_ajoutee')
    readonly_fields = ('date_ajoutee',)

    def save_model(self, request, obj, form, change):
        # Remplit automatiquement l'utilisateur connecté si vide
        if not obj.utilisateur_id:
            obj.utilisateur = request.user
        super().save_model(request, obj, form, change)
