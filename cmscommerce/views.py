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
from django.core.paginator import Paginator, EmptyPage


from .models import User, Product, Seller, Category, Cart, CartItem


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
        # print(f"role is: {role}")

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
            elif role == "Customer":
                # If the user is a customer, create a Cart instance associated with the user
                # pylint: disable=no-member
                Cart.objects.create(customer=user.customer)

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
            # print(f"user's token from login_view: {token}")
            login(request, user)
            return JsonResponse(
                {
                    "message": "User logged in successfully",
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
    # print("request.user: ", request.user)
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
        page_number = request.GET.get("page", 1)
        products_per_page = request.GET.get("per_page", 10)
        # print(f"page_number: {page_number};;; products_per_page: {products_per_page}")
        try:
            # print(f"seller_id: {seller_id}")
            # pylint: disable=no-member
            seller_user = User.objects.get(pk=seller_id)
            seller = Seller.objects.get(user=seller_user)
            products = Product.objects.filter(seller=seller).order_by("pk")

            paginator = Paginator(products, products_per_page)

            try:
                page_products = paginator.page(page_number)
            except EmptyPage:
                page_products = paginator.page(
                    1
                )  # Handle out-of-range pages by returning the first page

            total_pages = paginator.num_pages
            # print(f"total_pages: {total_pages}")

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
            # print(f"seller products json are: {products_json}")
            logout(request)
            return JsonResponse(
                {
                    "message": "Seller dashboard data retrieved successfully",
                    "products": products_json,
                    "pagination_info": {
                        "total_pages": total_pages,
                        "current_page": page_number,
                        "products_per_page": products_per_page,
                        "has_next": page_products.has_next(),
                        "has_previous": page_products.has_previous(),
                    },
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

        try:
            float_price = float(price)
            if float_price < 0:
                return JsonResponse(
                    {"error": "Price must be a positive number"}, status=400
                )
        except ValueError:
            return JsonResponse({"error": "Price must be a valid number"}, status=400)

        if not stock.isdigit() or int(stock) < 0:
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
        page_number = request.GET.get("page", 1)
        products_per_page = request.GET.get("per_page", 10)
        # print(f"page_number: {page_number};;; products_per_page: {products_per_page}")

        try:
            # pylint: disable=no-member
            products = Product.objects.all().order_by("pk")

            paginator = Paginator(products, products_per_page)

            try:
                page_products = paginator.page(page_number)
            except EmptyPage:
                page_products = paginator.page(
                    1
                )  # Handle out-of-range pages by returning the first page

            total_pages = paginator.num_pages
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
                    "pagination_info": {
                        "total_pages": total_pages,
                        "current_page": page_number,
                        "products_per_page": products_per_page,
                        "has_next": page_products.has_next(),
                        "has_previous": page_products.has_previous(),
                    },
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse(
                {"error": "Couldn't retrieve products. Error: " + str(e)}, status=500
            )


@role_required("Seller")
def delete_product(request, product_id):
    if request.method == "DELETE":
        try:
            # pylint: disable=no-member
            product = Product.objects.get(pk=product_id)
            product.delete()
            return JsonResponse({"message": "Product deleted successfully"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse(
                {"error": "Product with provided ID does not exist."}, status=400
            )
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)


@role_required("Seller")
def update_product(request, product_id):
    if request.method == "POST":
        try:
            # pylint: disable=no-member
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return JsonResponse(
                {"error": "Product with provided ID does not exist."}, status=400
            )
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

        try:
            float_price = float(price)
            if float_price < 0:
                return JsonResponse(
                    {"error": "Price must be a positive number"}, status=400
                )
        except ValueError:
            return JsonResponse({"error": "Price must be a valid number"}, status=400)

        if not stock.isdigit() or int(stock) < 0:
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

        try:
            product.name = name
            product.brand = brand
            product.description = description
            product.base_price = base_price
            product.price = price
            product.stock = stock
            product.category = category
            product.seller = seller
            if image:
                product.image = image

            product.save()

        except IntegrityError:
            return JsonResponse({"error": "Product couldn't be updated"}, status=400)

        return JsonResponse(
            {
                "message": "Product updated successfully",
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


@role_required("Customer")
def add_to_cart(request, product_id):
    """
    View for adding a product to the shopping cart for a customer.
    """
    if request.method == "POST":
        customer = request.user.customer

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return JsonResponse(
                {"error": "Product with provided ID does not exist."},
                status=400
            )

        quantity = int(request.POST.get("quantity", 1))

        # Check if the product is already in the customer's cart
        cart = Cart.objects.get(customer=customer)
        if CartItem.objects.filter(cart=cart, product=product).exists():
            return JsonResponse(
                {"error": "Product is already in the cart."},
                status=400
            )

        # Add the product to the cart
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)

        return JsonResponse(
            {"message": "Product added to cart successfully."},
            status=200
        )
    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=405
        )

@role_required("Customer")
def remove_from_cart(request, product_id):
    """
    View for removing a product from the shopping cart for a customer.
    """
    if request.method == "POST":
        customer = request.user.customer

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return JsonResponse(
                {"error": "Product with provided ID does not exist."},
                status=400
            )

        # Check if the product is in the customer's cart
        cart = Cart.objects.get(customer=customer)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return JsonResponse(
                {"error": "Product is not in the cart."},
                status=400
            )

        # Remove the product from the cart
        cart_item.delete()

        return JsonResponse(
            {"message": "Product removed from cart successfully."},
            status=200
        )
    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=405
        )

@role_required("Customer")
def update_cart(request, product_id):
    """
    View for updating the quantity of a product in the shopping cart for a customer.
    """
    if request.method == "POST":
        customer = request.user.customer

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return JsonResponse(
                {"error": "Product with provided ID does not exist."},
                status=400
            )

        new_quantity = int(request.POST.get("quantity", 1))

        # Check if the product is in the customer's cart
        cart = Cart.objects.get(customer=customer)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return JsonResponse(
                {"error": "Product is not in the cart."},
                status=400
            )

        # Update the quantity of the product in the cart
        cart_item.quantity = new_quantity
        cart_item.save()

        return JsonResponse(
            {"message": "Cart updated successfully."},
            status=200
        )
    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=405
        )