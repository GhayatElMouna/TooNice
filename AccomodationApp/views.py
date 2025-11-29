from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from .models import Accommodation, Chambre, Photo, Note, Reservation
from .forms import NoteForm

# -------------------------
# LISTE DES HÉBERGEMENTS
# -------------------------
class AccommodationListView(ListView):
    model = Accommodation
    template_name = 'AccommodationApp/accommodations_list.html'
    context_object_name = 'accommodations'
    paginate_by = 9  # 9 logements par page
    ordering = ['-date_ajoutee']  # Les plus récents en premier
    
    def get_queryset(self):
        """Retourne les accommodations triées par date d'ajout (plus récents en premier)"""
        queryset = super().get_queryset()
        return queryset.filter(est_actif=True).order_by('-date_ajoutee')
    
    def get_context_data(self, **kwargs):
        """Ajoute des informations supplémentaires au contexte"""
        context = super().get_context_data(**kwargs)
        # S'assurer que is_paginated est disponible
        context['is_paginated'] = self.get_queryset().count() > self.paginate_by
        return context


# -------------------------
# DÉTAIL D'UN HÉBERGEMENT
# -------------------------
class AccommodationDetailView(DetailView):
    model = Accommodation
    template_name = 'AccommodationApp/accommodation_detail.html'
    context_object_name = 'accommodation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chambres'] = self.object.chambres.all()
        context['photos'] = self.object.photos.all()
        context['notes'] = self.object.notes.all().order_by('-date_ajoutee')
        context['note_moyenne'] = self.object.get_note_moyenne()
        context['nombre_avis'] = self.object.get_nombre_avis()
        
        # Vérifier si l'utilisateur connecté a déjà laissé un avis
        if self.request.user.is_authenticated:
            try:
                context['user_note'] = Note.objects.get(
                    utilisateur=self.request.user,
                    accommodation=self.object
                )
                context['note_form'] = NoteForm(instance=context['user_note'])
            except Note.DoesNotExist:
                context['user_note'] = None
                context['note_form'] = NoteForm()
        else:
            context['user_note'] = None
            context['note_form'] = None
        
        return context


# -------------------------
# FORMSETS POUR CHAMBRES ET PHOTOS
# -------------------------
ChambreFormSet = inlineformset_factory(
    Accommodation,
    Chambre,
    fields=['numero', 'type_chambre', 'description', 'nombre_lits', 'prix_nuit'],
    extra=1,
    can_delete=True
)

PhotoFormSet = inlineformset_factory(
    Accommodation,
    Photo,
    fields=['image'],
    extra=1,
    can_delete=True
)

# -------------------------
# CRÉER UN HÉBERGEMENT
# -------------------------
class AccommodationCreateView(LoginRequiredMixin, CreateView):
    model = Accommodation
    fields = ['titre', 'description', 'type', 'gouvernorat', 'prix', 'adresse', 'est_actif']
    template_name = 'AccommodationApp/accommodation_form.html'
    success_url = reverse_lazy('accommodation:list_accommodations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['chambre_formset'] = ChambreFormSet(self.request.POST, prefix='chambres')
            context['photo_formset'] = PhotoFormSet(self.request.POST, self.request.FILES, prefix='photos')
        else:
            context['chambre_formset'] = ChambreFormSet(prefix='chambres')
            context['photo_formset'] = PhotoFormSet(prefix='photos')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        chambre_formset = context['chambre_formset']
        photo_formset = context['photo_formset']
        
        # Valider les formsets avant de sauvegarder l'accommodation
        if chambre_formset.is_valid() and photo_formset.is_valid():
            # Sauvegarder l'accommodation d'abord
            response = super().form_valid(form)
            self.object.utilisateurs.add(self.request.user)
            
            # Sauvegarder les chambres
            chambre_formset.instance = self.object
            chambre_formset.save()
            
            # Sauvegarder les photos
            photo_formset.instance = self.object
            photo_formset.save()
            
            return response
        else:
            # Si les formsets ne sont pas valides, réafficher le formulaire avec les erreurs
            return self.form_invalid(form)


# -------------------------
# MODIFIER UN HÉBERGEMENT
# -------------------------
class AccommodationUpdateView(LoginRequiredMixin, UpdateView):
    model = Accommodation
    fields = ['titre', 'description', 'type', 'gouvernorat', 'prix', 'adresse', 'est_actif']
    template_name = 'AccommodationApp/accommodation_form.html'
    success_url = reverse_lazy('accommodation:list_accommodations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['chambre_formset'] = ChambreFormSet(
                self.request.POST,
                instance=self.object,
                prefix='chambres'
            )
            context['photo_formset'] = PhotoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix='photos'
            )
        else:
            context['chambre_formset'] = ChambreFormSet(
                instance=self.object,
                prefix='chambres'
            )
            context['photo_formset'] = PhotoFormSet(
                instance=self.object,
                prefix='photos'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        chambre_formset = context['chambre_formset']
        photo_formset = context['photo_formset']
        
        # Valider les formsets avant de sauvegarder l'accommodation
        if chambre_formset.is_valid() and photo_formset.is_valid():
            # Sauvegarder l'accommodation
            response = super().form_valid(form)
            
            # Sauvegarder les chambres
            chambre_formset.save()
            
            # Sauvegarder les photos
            photo_formset.save()
            
            return response
        else:
            # Si les formsets ne sont pas valides, réafficher le formulaire avec les erreurs
            return self.form_invalid(form)


# -------------------------
# SUPPRIMER UN HÉBERGEMENT
# -------------------------
class AccommodationDeleteView(LoginRequiredMixin, DeleteView):
    model = Accommodation
    template_name = 'AccommodationApp/accommodation_confirm_delete.html'
    success_url = reverse_lazy('accommodation:list_accommodations')


# -------------------------
# CRUD POUR LES CHAMBRES
# -------------------------
class ChambreCreateView(LoginRequiredMixin, CreateView):
    model = Chambre
    fields = ['accommodation', 'numero', 'type_chambre', 'description', 'nombre_lits', 'prix_nuit']
    template_name = 'AccommodationApp/chambre_form.html'
    success_url = reverse_lazy('accommodation:list_accommodations')


class ChambreUpdateView(LoginRequiredMixin, UpdateView):
    model = Chambre
    fields = ['accommodation', 'numero', 'type_chambre', 'description', 'nombre_lits', 'prix_nuit']
    template_name = 'AccommodationApp/chambre_form.html'
    success_url = reverse_lazy('accommodation:list_accommodations')


class ChambreDeleteView(LoginRequiredMixin, DeleteView):
    model = Chambre
    template_name = 'AccommodationApp/chambre_confirm_delete.html'
    success_url = reverse_lazy('accommodation:list_accommodations')


# -------------------------
# CRUD POUR LES PHOTOS
# -------------------------
class PhotoCreateView(LoginRequiredMixin, CreateView):
    model = Photo
    fields = ['accommodation', 'image']
    template_name = 'AccommodationApp/photo_form.html'
    success_url = reverse_lazy('accommodation:list_accommodations')


class PhotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Photo
    template_name = 'AccommodationApp/photo_confirm_delete.html'
    success_url = reverse_lazy('accommodation:list_accommodations')


# -------------------------
# AVIS / NOTES
# -------------------------
class NoteCreateUpdateView(LoginRequiredMixin, View):
    """Vue pour créer ou mettre à jour un avis"""
    
    def post(self, request, accommodation_id):
        accommodation = get_object_or_404(Accommodation, pk=accommodation_id)
        
        # Vérifier si l'utilisateur a déjà laissé un avis
        try:
            note = Note.objects.get(
                utilisateur=request.user,
                accommodation=accommodation
            )
            form = NoteForm(request.POST, instance=note)
            is_update = True
        except Note.DoesNotExist:
            note = None
            form = NoteForm(request.POST)
            is_update = False
        
        if form.is_valid():
            note_obj = form.save(commit=False)
            note_obj.utilisateur = request.user
            note_obj.accommodation = accommodation
            note_obj.save()
            
            if is_update:
                messages.success(request, 'Votre avis a été mis à jour avec succès!')
            else:
                messages.success(request, 'Votre avis a été ajouté avec succès!')
        else:
            messages.error(request, 'Erreur lors de l\'enregistrement de votre avis.')
        
        return redirect('accommodation:accommodation_detail', pk=accommodation_id)


# -------------------------
# DISPONIBILITÉS / CALENDRIER
# -------------------------
class DisponibiliteView(View):
    """Vue pour récupérer les disponibilités d'une accommodation en JSON"""
    
    def get(self, request, accommodation_id):
        accommodation = get_object_or_404(Accommodation, pk=accommodation_id)
        
        # Récupérer toutes les dates occupées
        dates_occupees = accommodation.get_dates_occupees()
        
        # Formater les dates pour le calendrier
        dates_occupees_str = [date_obj.strftime('%Y-%m-%d') for date_obj in dates_occupees]
        
        # Récupérer les réservations par chambre pour plus de détails
        reservations_by_chambre = {}
        for chambre in accommodation.chambres.all():
            reservations = chambre.reservations.filter(
                statut__in=['en_attente', 'confirmee']
            ).values('date_debut', 'date_fin', 'statut')
            reservations_by_chambre[chambre.id] = [
                {
                    'date_debut': res['date_debut'].strftime('%Y-%m-%d'),
                    'date_fin': res['date_fin'].strftime('%Y-%m-%d'),
                    'statut': res['statut']
                }
                for res in reservations
            ]
        
        return JsonResponse({
            'dates_occupees': dates_occupees_str,
            'reservations_by_chambre': reservations_by_chambre,
            'accommodation_id': accommodation.id
        })
