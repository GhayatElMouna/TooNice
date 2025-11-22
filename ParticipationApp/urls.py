from django.urls import path
from . import views

app_name = 'participation'

urlpatterns = [
    path('register/<int:event_id>/', views.register_event, name='register_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('update/<int:participation_id>/', views.update_seats, name='update_seats'),
    path('delete/<int:participation_id>/', views.delete_participation, name='delete_participation'),
    path('past-events/', views.past_events, name='past_events'),
    path('confirm/<int:participation_id>/', views.confirm_reservation, name='confirm_reservation'),
    path("post-events/", views.post_events, name="post_events"),
    path('rate/<int:event_id>/', views.rate_event, name='rate_event'),



]

