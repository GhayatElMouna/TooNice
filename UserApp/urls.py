# UserApp/urls.py
from django.urls import path
from .views import *


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('signin/', SignInView.as_view(), name='user_signin'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('home/', IndexAuthView.as_view(), name='index_auth'),  # Page connectée
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
]