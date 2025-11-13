from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

#from UserApp .views import RegisterView, logout_view



urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('blog/', include('BlogApp.urls')),
    path('reservations/', include('reservations.urls')),

    #khedmet user
    path('', include('UserApp.urls')),  # ← Inclut /signin/
]
# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)