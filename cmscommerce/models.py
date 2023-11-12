from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    USER_ROLES = [
        ("Seller", "Seller"),
        ("Customer", "Customer"),
    ]
    role = models.CharField(max_length=10, choices=USER_ROLES, default="Customer")


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    billing_address = models.TextField()
    shipping_address = models.TextField()
    payment_information = models.TextField()


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50)
    description = models.TextField()


class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to="product_images/")


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    images = models.ManyToManyField(ProductImage)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, related_name="products"
    )


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderItem")
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_information = models.TextField()
    status = models.CharField(max_length=20)


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="CartItem")
    quantity = models.PositiveIntegerField()


class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()