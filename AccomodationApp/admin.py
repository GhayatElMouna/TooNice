from django.contrib import admin
from .models import Accommodation, Photo, Chambre

# Inline pour afficher les photos dans l'admin d'Accommodation
class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

# Inline pour afficher les chambres dans l'admin d'Accommodation
class ChambreInline(admin.TabularInline):
    model = Chambre
    extra = 1
    fields = ('numero', 'type_chambre', 'nombre_lits', 'prix_nuit')
    show_change_link = True

@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type', 'gouvernorat','prix', 'est_actif', 'nombre_chambres_display', 'date_ajoutee')
    list_filter = ('type', 'gouvernorat', 'est_actif', 'date_ajoutee')
    search_fields = ('titre', 'description', 'adresse')
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'type', 'gouvernorat', 'adresse', 'prix', 'est_actif')
        }),
    )
    # Garder filter_horizontal mais l'enlever du fieldsets pour qu'il ne soit pas visible
    filter_horizontal = ('utilisateurs',)
    inlines = [ChambreInline, PhotoInline]
    readonly_fields = ('date_ajoutee',)
    
    def get_fieldsets(self, request, obj=None):
        """Surcharge pour cacher les utilisateurs de l'interface"""
        fieldsets = super().get_fieldsets(request, obj)
        # Retourner uniquement les fieldsets visibles
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        """Surcharge pour cacher le champ utilisateurs dans le formulaire"""
        form = super().get_form(request, obj, **kwargs)
        # Cacher le champ utilisateurs mais le garder fonctionnel
        if 'utilisateurs' in form.base_fields:
            form.base_fields['utilisateurs'].widget = forms.MultipleHiddenInput()
        return form
    
    def nombre_chambres_display(self, obj):
        """Affiche le nombre de chambres"""
        return obj.get_nombre_chambres()
    nombre_chambres_display.short_description = 'Nombre de chambres'
    


@admin.register(Chambre)
class ChambreAdmin(admin.ModelAdmin):
    list_display = ('numero', 'accommodation', 'type_chambre', 'nombre_lits', 'prix_nuit','date_ajoutee')
    list_filter = ('type_chambre', 'accommodation', 'date_ajoutee')
    search_fields = ('numero', 'accommodation__titre', 'description')
    fieldsets = (
        ('Informations de la chambre', {
            'fields': ('accommodation', 'numero', 'type_chambre', 'description')
        }),
        ('Capacité et prix', {
            'fields': ('nombre_lits', 'prix_nuit')
        })
    )
    readonly_fields = ('date_ajoutee',)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'accommodation', 'image')
    list_filter = ('accommodation',)
    search_fields = ('accommodation__titre',)