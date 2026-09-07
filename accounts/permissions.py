"""Role hierarchy checks (SRS §2.3)."""

from functools import wraps
from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import Role

ROLE_HIERARCHY = {
    Role.GUEST: 0,
    Role.VUB_NETWORK: 1,
    Role.MEMBER: 2,
    Role.PUBLISHER: 3,
    Role.MODERATOR: 4,
    Role.ADMINISTRATOR: 5,
}


def get_user_role(request):
    """
    Determine the effective role of the actor making the request.
    - If user is authenticated, not locked, and confirmed: user.role
    - Else if request.vub_network_mode is True: Role.VUB_NETWORK
    - Else: Role.GUEST
    """
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        if not getattr(user, "is_locked", False) and getattr(user, "is_confirmed", False):
            return user.role
        if getattr(request, "vub_network_mode", False):
            return Role.VUB_NETWORK
        return Role.GUEST

    if getattr(request, "vub_network_mode", False):
        return Role.VUB_NETWORK

    return Role.GUEST


def has_role(request, *roles):
    """Check if the user's effective role satisfies the required roles under inheritance."""
    effective_role = get_user_role(request)
    current_level = ROLE_HIERARCHY.get(effective_role, 0)
    if not roles:
        return True
    required_level = min(ROLE_HIERARCHY.get(r, 0) for r in roles)
    return current_level >= required_level


def require_role(*roles):
    """
    Decorator requiring the request to have at least the privileges of one of the specified roles.
    If unauthorized:
      - If user is not authenticated: redirect to login
      - If authenticated: HTTP 403 Forbidden
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if has_role(request, *roles):
                return view_func(request, *args, **kwargs)

            if not request.user.is_authenticated:
                from django.shortcuts import resolve_url
                login_url = resolve_url(settings.LOGIN_URL)
                return redirect(f"{login_url}?next={request.path}")
            return HttpResponseForbidden("You do not have permission to access this resource.")

        return wrapped

    return decorator

