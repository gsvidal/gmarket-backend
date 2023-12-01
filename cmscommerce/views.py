from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import IntegrityError
from django.urls import reverse
import json
from helpers import seller_required
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.authtoken.models import Token

from .models import User


# Create your views here.
def index(request) -> HttpResponse:
    """
    View for the index page.

    Returns:
        HttpResponse: A simple HTTP response with the message "hello world".
    """
    return HttpResponse("hello world")


def register(request) -> JsonResponse:
    """
    View for registering a new user.
    Returns:
        JsonResponse: A JSON response with the message "User created successfully".
    """
    if request.method == "POST":
        data = json.loads(request.body)
        print(f"data sent from frontend: {data}")
        username = data.get("username")

        if username.strip() == "":
            return JsonResponse(
                {"error": "Username field must not be empty."}, status=400
            )

        password = data.get("password")

        if password.strip() == "":
            return JsonResponse(
                {"error": "Password field must not be empty."}, status=400
            )

        confirmation = data.get("confirmPassword")
        if len(password) < 6:
            return JsonResponse(
                {"error": "Password must be at least 6 characters long."}, status=400
            )

        # Ensure password matches confirmation
        if password != confirmation:
            return JsonResponse({"error": "Passwords must match."}, status=400)

        # User role
        role = data.get("role")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, password)
            user.role = role
            user.save()

            # After the user is created, create a token for the user
            # pylint: disable=no-member
            token = Token.objects.create(user=user)
            print(f"usersss token - from register: {token}")

        except IntegrityError:
            return JsonResponse({"error": "Username already taken."}, status=400)

        login(request, user)
        return JsonResponse(
            {
                "message": "User created successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "created_at": user.created_at,
                },
                "token": token.key,
            },
            status=200,
        )
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)


def login_view(request) -> JsonResponse:
    """
    View for logging in a user.
    Returns:
        JsonResponse: A JSON response with the message "User logged in successfully".
    """

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            return JsonResponse(
                {"error": "Invalid username and/or password."}, status=400
            )


def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully."}, status=200)


@seller_required
def seller_dashboard(request):
    print(f"seller user is: {request.user}")
    print(f"seller user is: {request.user.is_authenticated}")
    print(f"seller user is: {request.user.role}")

    if request.method == "GET":
        return JsonResponse({"message": "Seller dashboard from back"}, status=200)