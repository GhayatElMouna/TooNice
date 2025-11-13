from django.urls import path
from .views import (
    ReservationListView,
    ReservationDetailView,
    ReservationCreateView,
    ReservationUpdateView,
    ReservationDeleteView,
)

app_name = "reservations"

urlpatterns = [
    path("", ReservationListView.as_view(), name="list"),
    path("add/", ReservationCreateView.as_view(), name="create"),
    path("<int:pk>/", ReservationDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", ReservationUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ReservationDeleteView.as_view(), name="delete"),
]
