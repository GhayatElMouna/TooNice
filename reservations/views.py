from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Reservation,Logement
from .forms import ReservationForm

import json


class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "ReservationsApp/reservation_list.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class ReservationDetailView(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = "ReservationsApp/reservation_detail.html"
    context_object_name = "reservation"


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = "ReservationsApp/reservation_form.html"
    success_url = reverse_lazy("reservations:list")

    def form_valid(self, form):
        # Associer l'utilisateur
        form.instance.user = self.request.user

        # Récupérer les données déjà valides du formulaire
        logement = form.cleaned_data["logement"]
        date_debut = form.cleaned_data["date_debut"]
        date_fin = form.cleaned_data["date_fin"]

        # Calculer le nombre de nuits
        nb_nuits = (date_fin - date_debut).days
        if nb_nuits < 0:
            nb_nuits = 0  # sécurité, mais normalement géré par la validation du form

        # Calculer le prix total = nb_nuits * prix_par_nuit du logement
        form.instance.prix_total = nb_nuits * logement.prix_par_nuit

        # Maintenant on laisse Django sauvegarder
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logements = Logement.objects.all()
        context["logement_prices_json"] = json.dumps({
            logement.id: float(logement.prix_par_nuit) for logement in logements
        })
        return context
class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = "ReservationsApp/reservation_form.html"
    success_url = reverse_lazy("reservations:list")

    def form_valid(self, form):
        logement = form.cleaned_data["logement"]
        date_debut = form.cleaned_data["date_debut"]
        date_fin = form.cleaned_data["date_fin"]

        nb_nuits = (date_fin - date_debut).days
        if nb_nuits < 0:
            nb_nuits = 0

        form.instance.prix_total = nb_nuits * logement.prix_par_nuit

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logements = Logement.objects.all()
        context["logement_prices_json"] = json.dumps({
            logement.id: float(logement.prix_par_nuit) for logement in logements
        })
        return context



class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = "ReservationsApp/reservation_confirm_delete.html"
    success_url = reverse_lazy("reservations:list")
