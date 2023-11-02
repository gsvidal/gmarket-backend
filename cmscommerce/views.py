from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.db import IntegrityError
from django.urls import reverse
import json
from helpers import seller_required

from .models import User


# Create your views here.
def index(request):
    return HttpResponse("hello world")


def register(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        if username.strip() == "":
            return JsonResponse(
                {"error": "Username field must not be empty."}, status=400
            )

        email = data.get("email")
        if email.strip() == "":
            return JsonResponse({"error": "Email field must not be empty."}, status=400)

        # Ensure password matches confirmation
        password = data.get("password")
        confirmation = data.get("confirmation")
        if password != confirmation:
            return JsonResponse({"error": "Passwords must match."}, status=400)
        
        # User role
        role = data.get("role")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.role = role
            user.save()
        except IntegrityError:
            return JsonResponse({"error": "Username already taken."}, status=400)
        # login(request, user)
        return JsonResponse({"message": "User registered successfully."}, status=200)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)


@seller_required
def seller_dashboard(request):
    return HttpResponse("Seller dashboard")
