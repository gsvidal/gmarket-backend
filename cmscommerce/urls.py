from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login_view", views.login_view, name="login_view"),
    path("logout_view", views.logout_view, name="logout_view"),
    path(
        "seller_dashboard/<int:seller_id>",
        views.seller_dashboard,
        name="seller_dashboard",
    ),
    path("categories", views.categories, name="categories"),
    path("create_product", views.create_product, name="create_product"),
    path("all_products", views.all_products, name="all_products"),
]
