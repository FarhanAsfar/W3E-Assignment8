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

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("external_id", "title", "location", "address", "created_at")
    list_filter = ("location",)
    search_fields = ("external_id", "title", "address", "location__name")
    ordering = ("-created_at",)

    inlines = [PropertyImageInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance
        primary_count = obj.images.filter(is_primary = True).count()

        if primary_count > 1:
            return ValidationError("Select only one primary image for a property")