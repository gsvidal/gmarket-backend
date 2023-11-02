from django.http import HttpResponse
from django.shortcuts import render
from helpers import seller_required


# Create your views here.
def index(request):
    return HttpResponse("hello world")


@seller_required
def seller_dashboard(request):
    return HttpResponse("Seller dashboard")
