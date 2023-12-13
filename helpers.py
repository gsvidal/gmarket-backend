from functools import wraps
from django.http import HttpResponseForbidden
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


# Create the custom decorator
def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token_auth = TokenAuthentication()

            try:
                user_auth_tuple = token_auth.authenticate(request)
            except AuthenticationFailed:
                return HttpResponseForbidden("Invalid token.")

            if user_auth_tuple is not None:
                request.user = user_auth_tuple[0]

            if request.user.is_authenticated and (request.user.role == role or role == "any"):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden(
                    "You don't have permission to access this page."
                )

        return _wrapped_view
    return decorator