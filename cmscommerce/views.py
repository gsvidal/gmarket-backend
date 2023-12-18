from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import IntegrityError
from django.urls import reverse
import json
from helpers import role_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.core import serializers


from .models import User, Product, Seller, Category


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
        print(f"role is: {role}")

        if role is None:
            return JsonResponse({"error": "Role is required."}, status=400)

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, "", password)
            user.role = role
            user.save()

            # If the user is a seller, create a Seller instance associated with the user
            if role == "Seller":
                # pylint: disable=no-member
                Seller.objects.create(user=user)

            # After the user is created, create a token for the user
            # pylint: disable=no-member
            token = Token.objects.create(user=user)

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
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Tries to get an existing token for the user. If a token doesn't exist, it creates a new one.
            # pylint: disable=no-member
            token, created = Token.objects.get_or_create(user=user)
            print(f"user's token from login_view: {token}")
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
            return JsonResponse(
                {"error": "Invalid username and/or password."}, status=400
            )


@role_required("any")
def logout_view(request):
    print("request.user: ", request.user)
    try:
        # Check if the user exists in the backend
        User.objects.get(pk=request.user.id)

        # pylint: disable=no-member
    except User.DoesNotExist:
        # If the user does not exist, clear the session
        logout(request)
        return JsonResponse({"message": "User does not exist."}, status=401)

    # If the user exists, log out as usual
    logout(request)
    return JsonResponse({"message": "Logged out successfully."}, status=200)


@role_required("Seller")
def seller_dashboard(request, seller_id):
    if request.method == "GET":
        try:
            print(f"seller_id: {seller_id}")
            # pylint: disable=no-member
            seller_user = User.objects.get(pk=seller_id)
            seller = Seller.objects.get(user=seller_user)
            products = Product.objects.filter(seller=seller)

            # Serialize the products
            products_json = [
                {
                    "id": p.pk,
                    "name": p.name,
                    "brand": p.brand,
                    "description": p.description,
                    "base_price": str(p.base_price),
                    "price": str(p.price),
                    "stock": p.stock,
                    "image": p.image.url if p.image else None,
                    "category": {
                        "id": p.category.id,
                        "name": p.category.name,
                        "code": p.category.code,
                    },
                    "seller": {
                        "id": p.seller.id,
                        "username": p.seller.user.username,
                    },
                }
                for p in products
            ]
            print(f"seller products json are: {products_json}")
            return JsonResponse(
                {
                    "message": "Seller dashboard data retrieved successfully",
                    "products": products_json,
                },
                status=200,
            )
        # pylint: disable=no-member
        except Seller.DoesNotExist:
            return JsonResponse(
                {"error": "Seller with provided ID does not exist."}, status=400
            )


@role_required("Seller")
def categories(request):
    if request.method == "GET":
        # pylint: disable=no-member
        categories_data = Category.objects.all()
        categories_json = [
            {"id": c.pk, "name": c.name, "code": c.code} for c in categories_data
        ]
        return JsonResponse(
            {
                "message": "Categories retrieved successfully",
                "categories": categories_json,
            },
            status=200,
        )


@role_required("Seller")
def create_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        brand = request.POST.get("brand")
        description = request.POST.get("description")
        base_price = request.POST.get("base_price")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        category_code = request.POST.get("category_code")
        seller_id = int(request.POST.get("seller_id"))
        image = request.FILES.get("image")  # Use request.FILES for file fields

        # Validate inputs
        fields_to_validate = [
            {"field": name, "message": "Name is required"},
            {"field": brand, "message": "Brand is required"},
            {"field": description, "message": "Description is required"},
            {"field": base_price, "message": "Base price is required"},
            {"field": price, "message": "Price is required"},
            {"field": stock, "message": "Stock is required"},
        ]

        for field in fields_to_validate:
            if not field["field"]:
                return JsonResponse({"error": field["message"]}, status=400)

        if float(price) < 0:
            return JsonResponse(
                {"error": "Price must be a positive number"}, status=400
            )

        if int(stock) < 0:
            return JsonResponse(
                {"error": "Stock must be a positive integer"}, status=400
            )

        if image:
            if not image.name.endswith((".jpg", ".png")):
                return JsonResponse(
                    {"error": "Image must be a .jpg or .png file."}, status=400
                )
            if image.size > 2 * 1024 * 1024:
                return JsonResponse(
                    {"error": "Image must be less than or equal to 2MB."}, status=400
                )

        try:
            seller_user = User.objects.get(pk=seller_id)

        # pylint: disable=no-member
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "Seller with provided ID does not exist."}, status=400
            )

        # pylint: disable=no-member
        seller = Seller.objects.get(user=seller_user)
        # If no category_code is provided, use the "no-category" category
        if not category_code:
            category_code = "no-category"

        # pylint: disable=no-member
        category = Category.objects.get(code=category_code)

        # Attempt to create new product
        # pylint: disable=no-member
        try:
            product = Product.objects.create(
                name=name,
                brand=brand,
                description=description,
                base_price=base_price,
                price=price,
                stock=stock,  # Include the stock value
                category=category,
                seller=seller,
                image=image,
            )

        except IntegrityError:
            return JsonResponse({"error": "Product already exists."}, status=400)

        return JsonResponse(
            {
                "message": "Product created successfully",
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "description": product.description,
                    "base_price": product.base_price,
                    "price": product.price,
                    "stock": product.stock,  # Return the stock value
                    "category": {
                        "id": product.category.id,
                        "name": product.category.name,
                        "code": product.category.code,
                    },
                    "seller": {
                        "id": product.seller.id,
                        "username": product.seller.user.username,
                    },
                    "image": product.image.url if product.image else None,
                    # Return the URL of the image
                },
            },
            status=200,
        )
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)


def all_products(request):
    if request.method == "GET":
        try:
            # pylint: disable=no-member
            products = Product.objects.all()
            products_json = [
                {
                    "id": p.pk,
                    "name": p.name,
                    "brand": p.brand,
                    "description": p.description,
                    "base_price": str(p.base_price),
                    "price": str(p.price),
                    "stock": p.stock,
                    "image": p.image.url if p.image else None,
                    "category": {
                        "id": p.category.id,
                        "name": p.category.name,
                        "code": p.category.code,
                    },
                    "seller": {
                        "id": p.seller.id,
                        "username": p.seller.user.username,
                    },
                }
                for p in products
            ]
            return JsonResponse(
                {
                    "message": "Products retrieved successfully",
                    "products": products_json,
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse(
                {"error": "Couldn't retrieve products. Error: " + str(e)}, status=500
            )
