"""Role hierarchy checks (SRS §2.3). Currently a no-op; real checks come later."""

from functools import wraps


def require_role(*_roles):
    """Placeholder decorator. Allows every request until authorization is implemented."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
