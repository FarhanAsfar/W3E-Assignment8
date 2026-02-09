from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet, PropertyViewSet


router = DefaultRouter()
router.register(r"locations", LocationViewSet, basename="locations")
router.register(r"properties", PropertyViewSet, basename="properties")


urlpatterns = [
    path("", include(router.urls)),
]