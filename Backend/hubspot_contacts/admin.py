from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'hubspot_id')  # Fields to display in the admin list view
    search_fields = ('email', 'first_name', 'last_name')  # Fields to enable search functionality
    list_filter = ('first_name', 'last_name')  # Fields to filter by in the admin list view
admin.site.register(Contact , ContactAdmin )