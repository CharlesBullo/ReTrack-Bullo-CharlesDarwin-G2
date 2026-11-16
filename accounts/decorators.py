from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .utils import get_profile


def role_required(role):
    """Logged-out users go to login. Users with a different role go back to their own dashboard."""

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if get_profile(request.user).role != role:
                messages.error(request, "You don't have access to that page.")
                return redirect("accounts:dashboard")
            return view(request, *args, **kwargs)

        return login_required(wrapper)

    return decorator
