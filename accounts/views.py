from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_http_methods

from orgs.models import DepartmentGroup
from .models import Role, User
from .permissions import require_role
from .services import confirm_account, issue_confirmation_token


class StubLoginView(LoginView):
    template_name = "accounts/login.html"

    def form_valid(self, form):
        user = form.get_user()
        if getattr(user, "is_locked", False):
            form.add_error(None, "This account has been locked. Please contact the administrator.")
            return self.form_invalid(form)
        if not getattr(user, "is_confirmed", False):
            form.add_error(None, "Account confirmation is pending. Please confirm your account first.")
            return self.form_invalid(form)
        return super().form_valid(form)


class StubLogoutView(View):
    def post(self, request, *args, **kwargs):
        is_vub = getattr(request, "vub_network_mode", False)
        logout(request)
        if is_vub:
            return redirect("publications:search")
        return redirect("accounts:login")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@require_http_methods(["GET", "POST"])
def register(request):
    departments = DepartmentGroup.objects.all().order_by("name")
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        email = request.POST.get("email", "").strip()
        university = request.POST.get("university", "").strip()
        dept_id = request.POST.get("department")

        errors = []
        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append("A user with that username already exists.")

        if not password:
            errors.append("Password is required.")
        if not email:
            errors.append("Email is required.")
        elif "@" not in email or "." not in email:
            errors.append("Please enter a valid email address.")

        dept = None
        if dept_id:
            dept = DepartmentGroup.objects.filter(pk=dept_id).first()

        if errors:
            return render(
                request,
                "accounts/register.html",
                {
                    "departments": departments,
                    "errors": errors,
                    "form_data": request.POST,
                },
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            university=university,
            department=dept,
            role=Role.GUEST,
            is_confirmed=False,
        )

        token = issue_confirmation_token(user)
        messages.success(
            request,
            f"Registration successful! Your confirmation token is: {token}. Please enter it below to activate your account.",
        )
        return redirect("accounts:confirm")

    return render(request, "accounts/register.html", {"departments": departments})


@require_http_methods(["GET", "POST"])
def confirm(request):
    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        success, message = confirm_account(token)
        if success:
            messages.success(request, message)
            return redirect("accounts:login")
        messages.error(request, message)
        return render(request, "accounts/confirm.html", {"error": message, "entered_token": token})

    return render(request, "accounts/confirm.html")


@require_http_methods(["GET", "POST"])
def network_mode(request):
    if request.method == "POST":
        mode = request.POST.get("mode", "")
        is_vub = (mode == "vub")
        request.session["vub_network_mode"] = is_vub
        messages.success(
            request,
            f"Network mode updated to: {'VUB Network (VUB-Network User privileges)' if is_vub else 'General Internet'}",
        )
        return redirect("accounts:network_mode")

    return render(
        request,
        "accounts/network_mode.html",
        {"vub_network_mode": getattr(request, "vub_network_mode", False)},
    )


@require_role("moderator", "administrator")
@require_http_methods(["GET"])
def user_search(request):
    query = request.GET.get("q", "").strip()
    users = User.objects.select_related("department").all()

    # Moderator is restricted to their own department
    if request.user.role == Role.MODERATOR:
        users = users.filter(department=request.user.department)

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(role__icontains=query)
            | Q(department__name__icontains=query)
        )

    users = users.order_by("username")
    return render(
        request,
        "accounts/user_search.html",
        {"users": users, "query": query, "is_admin": request.user.role == Role.ADMINISTRATOR},
    )


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def user_create(request):
    departments = DepartmentGroup.objects.all().order_by("name")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        role = request.POST.get("role", Role.MEMBER)
        dept_id = request.POST.get("department")

        errors = []
        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append("Username already exists.")
        if not password:
            errors.append("Password is required.")
        if not email:
            errors.append("Email is required.")

        if errors:
            return render(
                request,
                "accounts/user_create.html",
                {"errors": errors, "departments": departments, "roles": Role.choices, "form_data": request.POST},
            )

        dept = DepartmentGroup.objects.filter(pk=dept_id).first() if dept_id else None
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            department=dept,
            role=role,
            is_confirmed=True,
        )
        messages.success(request, f"User '{username}' created successfully.")
        return redirect("accounts:user_search")

    return render(
        request,
        "accounts/user_create.html",
        {"departments": departments, "roles": Role.choices},
    )


@require_role("moderator", "administrator")
@require_http_methods(["GET", "POST"])
def user_edit(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    is_admin = request.user.role == Role.ADMINISTRATOR

    # Moderator boundary check
    if not is_admin:
        if target_user.department_id != request.user.department_id:
            return HttpResponseForbidden("Moderators may only edit users in their own department.")

    departments = DepartmentGroup.objects.all().order_by("name")

    if request.method == "POST":
        target_user.first_name = request.POST.get("first_name", "").strip()
        target_user.last_name = request.POST.get("last_name", "").strip()
        target_user.email = request.POST.get("email", "").strip()
        new_role = request.POST.get("role")

        if is_admin:
            dept_id = request.POST.get("department")
            target_user.department = DepartmentGroup.objects.filter(pk=dept_id).first() if dept_id else None
            target_user.is_locked = bool(request.POST.get("is_locked"))
            if new_role and new_role in dict(Role.choices):
                target_user.role = new_role
        else:
            # Moderator can only change between MEMBER and PUBLISHER
            if new_role:
                if new_role not in [Role.MEMBER, Role.PUBLISHER]:
                    return HttpResponseForbidden("Moderators can only set role to Member or Publisher.")
                target_user.role = new_role

        target_user.save()
        messages.success(request, f"User '{target_user.username}' updated successfully.")
        return redirect("accounts:user_search")

    # Limit available role choices for moderator
    if is_admin:
        available_roles = Role.choices
    else:
        available_roles = [(Role.MEMBER, "Member"), (Role.PUBLISHER, "Publisher")]

    return render(
        request,
        "accounts/user_edit.html",
        {
            "target_user": target_user,
            "departments": departments,
            "roles": available_roles,
            "is_admin": is_admin,
        },
    )


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def user_delete(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        username = target_user.username
        target_user.delete()
        messages.success(request, f"User '{username}' deleted successfully.")
        return redirect("accounts:user_search")

    return render(request, "accounts/user_delete.html", {"target_user": target_user})

