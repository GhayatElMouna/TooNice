from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display=("user_id","username","first_name","last_name","email","role")
    search_fields=("user_id","username","email")
# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.site_header="User Managment Dadhboard"
admin.site.site_title="User"
admin.site.index_title="Dashboard"



