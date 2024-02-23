from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


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
    path(
        "delete_product/<int:product_id>", views.delete_product, name="delete_product"
    ),
    path(
        "update_product/<int:product_id>", views.update_product, name="update_product"
    ),
    path("add_to_cart/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    path(
        "update_quantity/<int:product_id>",
        views.update_quantity,
        name="update_quantity",
    ),
    path(
        "remove_from_cart/<int:product_id>",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
]


# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
