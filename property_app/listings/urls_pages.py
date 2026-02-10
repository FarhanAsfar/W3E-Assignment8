from django.urls import path
from . import views_pages

urlpatterns = [
    path("", views_pages.home, name="home"),
    path("properties/<slug:location_slug>/<slug:property_slug>/", views_pages.property_detail_page, name="property_detail_page"),
]
