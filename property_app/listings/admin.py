from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Location, Property, PropertyImage

# Register your models here.

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ("image", "is_primary", "alt_text")
    can_delete = True 