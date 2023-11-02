from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("seller/register", views.seller_dashboard, name="seller_dashboard")
    # API Routes
]
