from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Location, Property, 
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

        qs = Location.objects.filter(name__isstartswith=q).order_by("name")[:5]
        data = LocationSerializer(qs, many=True).data
        return Response({"results": data})