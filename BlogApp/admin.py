from django.contrib import admin
from .models import *
class ArticleAdmin(admin.ModelAdmin):
    list_display=('titre','description','type_media','date_publication')
    search_fields=('titre','description','type_media')
    list_filter=('type_media','date_publication')
    list_per_page=1
    
    def has_add_permission(self, request):
        """Disallow adding Articles through the admin interface."""
        return False
# Register your models here.
admin.site.register(Article,ArticleAdmin)



# Register your models here.
