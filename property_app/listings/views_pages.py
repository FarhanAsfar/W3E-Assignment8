from django.shortcuts import render


def home(request):
    return render(request, "listings/home.html")


def property_detail_page(request, pk: int):
    return render(request, "listings/property_detail.html", {"property_id": pk})
