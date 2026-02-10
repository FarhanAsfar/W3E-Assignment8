from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Location, Property 
from .serializers import (LocationSerializer, PropertyListSerializer, PropertyDetailSerializer,)


# Create your views here.
class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @action(detail=False, methods=["get"], url_path="autocomplete")
    def autocomplete(self, request):
        q = (request.query_params.get("q") or "").strip()
        if len(q) < 3:
            return Response({"results": []})

        qs = Location.objects.filter(name__icontains=q).order_by("name")[:5]
        data = LocationSerializer(qs, many=True).data
        return Response({"results": data})


class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Property.objects.select_related("location").prefetch_related("images").all() # prefetch_related-> include images in the initial fetch. it optimizes the search function, search results wil load with only 2 db queries.

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PropertyDetailSerializer
        return PropertyListSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        location_name = (self.request.query_params.get("location") or "").strip() #get the location from the url
                         
        if location_name:
            qs = qs.filter(location__name__iexact = location_name)
        return qs  