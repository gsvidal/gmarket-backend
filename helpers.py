from functools import wraps
from django.http import HttpResponseForbidden


# Create the custom decorator
def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated and has the 'Seller' role
        if request.user.is_authenticated and request.user.role == "Seller":
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(
                "You don't have permission to access this page."
            )

    return _wrapped_view
