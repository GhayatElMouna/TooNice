from django.urls import path
from . import views

app_name = 'accommodation'

urlpatterns = [
    # Liste des accommodations
    path('', views.AccommodationListView.as_view(), name='home'),
    path('accommodations/', views.AccommodationListView.as_view(), name='list_accommodations'),
    
    # Détail d'une accommodation
    path('accommodations/<int:pk>/', views.AccommodationDetailView.as_view(), name='accommodation_detail'),
    
    # CRUD Accommodation
    path('accommodations/create/', views.AccommodationCreateView.as_view(), name='accommodation_create'),
    path('accommodations/<int:pk>/update/', views.AccommodationUpdateView.as_view(), name='accommodation_update'),
    path('accommodations/<int:pk>/delete/', views.AccommodationDeleteView.as_view(), name='accommodation_delete'),
    
    # CRUD Chambre
    path('chambres/create/', views.ChambreCreateView.as_view(), name='chambre_create'),
    path('chambres/<int:pk>/update/', views.ChambreUpdateView.as_view(), name='chambre_update'),
    path('chambres/<int:pk>/delete/', views.ChambreDeleteView.as_view(), name='chambre_delete'),
    
    # CRUD Photo
    path('photos/create/', views.PhotoCreateView.as_view(), name='photo_create'),
    path('photos/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
]
