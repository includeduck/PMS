from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .permissions import require_role


class StubLoginView(LoginView):
    template_name = "accounts/login.html"


class StubLogoutView(LogoutView):
    next_page = "accounts:login"


@require_http_methods(["GET", "POST"])
def register(request):
    return render(request, "accounts/register.html")


@require_http_methods(["GET", "POST"])
def confirm(request):
    return render(request, "accounts/confirm.html")


@require_http_methods(["GET", "POST"])
def network_mode(request):
    return render(
        request,
        "accounts/network_mode.html",
        {"vub_network_mode": getattr(request, "vub_network_mode", False)},
    )


@require_role("moderator", "administrator")
@require_http_methods(["GET", "POST"])
def user_search(request):
    return render(request, "accounts/user_search.html")


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def user_create(request):
    return render(request, "accounts/user_create.html")


@require_role("moderator", "administrator")
@require_http_methods(["GET", "POST"])
def user_edit(request, pk):
    return render(request, "accounts/user_edit.html", {"user_id": pk})


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def user_delete(request, pk):
    return render(request, "accounts/user_delete.html", {"user_id": pk})
