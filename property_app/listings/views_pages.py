from django.shortcuts import render, get_object_or_404
from .models import Property


def home(request):
    return render(request, "listings/home.html")


def property_detail_page(request, location_slug, property_slug):
    prop = get_object_or_404(
        Property.objects.select_related("location"),
        location__slug = location_slug,
        slug = property_slug,
    )
    return render(request, "listings/property_detail.html", {"property_id": prop.id})
