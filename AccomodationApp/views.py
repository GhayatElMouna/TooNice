from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory
from .models import Accommodation, Chambre, Photo
from django.contrib.auth.mixins import LoginRequiredMixin

# -------------------------
# LISTE DES HÉBERGEMENTS
# -------------------------
class AccommodationListView(ListView):
    model = Accommodation
    template_name = 'AccommodationApp/accommodations_list.html'
    context_object_name = 'accommodations'
    paginate_by = 10


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
