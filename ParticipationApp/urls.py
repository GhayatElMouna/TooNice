from django.urls import path
from . import views

app_name = 'participation'

urlpatterns = [
    path('register/<int:event_id>/', views.register_event, name='register_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('update/<int:participation_id>/', views.update_seats, name='update_seats'),
    path('delete/<int:participation_id>/', views.delete_participation, name='delete_participation'),
]

