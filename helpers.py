from functools import wraps
from django.http import HttpResponseForbidden
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Create the custom decorator
def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Create an instance of TokenAuthentication
        token_auth = TokenAuthentication()

        try:
            # Try to authenticate the user
            user_auth_tuple = token_auth.authenticate(request)
        except AuthenticationFailed:
            return HttpResponseForbidden("Invalid token.")

        if user_auth_tuple is not None:
            # If the user was authenticated, replace the current user with the authenticated user
            request.user = user_auth_tuple[0]

        print(f"request:: {request.user}")
        print(f"request:: {request.user.is_authenticated}")
        print(f"request:: {request.user.role}")

        # Check if the user is authenticated and has the 'Seller' role
        if request.user.is_authenticated and request.user.role == "Seller":
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(
                "You don't have permission to access this page."
            )

    return _wrapped_view