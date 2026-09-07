from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import User
from accounts.permissions import require_role
from .models import DepartmentGroup


@require_role("administrator")
@require_http_methods(["GET"])
def group_search(request):
    query = request.GET.get("q", "").strip()
    groups = DepartmentGroup.objects.annotate(member_count=Count("members"))
    if query:
        groups = groups.filter(Q(name__icontains=query) | Q(description__icontains=query))
    groups = groups.order_by("name")
    return render(request, "orgs/group_search.html", {"groups": groups, "query": query})


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def group_create(request):
    users = User.objects.all().order_by("username")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        user_ids = request.POST.getlist("users")

        errors = []
        if not name:
            errors.append("Group name is required.")
        elif DepartmentGroup.objects.filter(name__iexact=name).exists():
            errors.append("A group with this name already exists.")

        if errors:
            return render(
                request,
                "orgs/group_create.html",
                {"errors": errors, "users": users, "form_data": request.POST},
            )

        group = DepartmentGroup.objects.create(name=name, description=description)
        if user_ids:
            User.objects.filter(pk__in=user_ids).update(department=group)

        messages.success(request, f"Group '{group.name}' created successfully.")
        return redirect("orgs:group_search")

    return render(request, "orgs/group_create.html", {"users": users})


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def group_edit(request, pk):
    group = get_object_or_404(DepartmentGroup, pk=pk)
    all_users = User.objects.all().order_by("username")
    current_member_ids = set(group.members.values_list("id", flat=True))

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        selected_user_ids = set(map(int, filter(None, request.POST.getlist("users"))))

        errors = []
        if not name:
            errors.append("Group name is required.")
        elif DepartmentGroup.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            errors.append("A group with this name already exists.")

        if errors:
            return render(
                request,
                "orgs/group_edit.html",
                {
                    "group": group,
                    "all_users": all_users,
                    "current_member_ids": current_member_ids,
                    "errors": errors,
                },
            )

        group.name = name
        group.description = description
        group.save()

        # Add newly selected users
        User.objects.filter(pk__in=selected_user_ids).update(department=group)
        # Remove unselected users
        group.members.exclude(pk__in=selected_user_ids).update(department=None)

        messages.success(request, f"Group '{group.name}' updated successfully.")
        return redirect("orgs:group_search")

    return render(
        request,
        "orgs/group_edit.html",
        {
            "group": group,
            "all_users": all_users,
            "current_member_ids": current_member_ids,
        },
    )


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def group_delete(request, pk):
    group = get_object_or_404(DepartmentGroup, pk=pk)
    member_count = group.members.count()

    if request.method == "POST":
        # Live membership check: must not delete a non-empty group
        if group.members.exists():
            error_msg = "Cannot delete group: group still has members. Reassign or remove members first."
            messages.error(request, error_msg)
            return render(
                request,
                "orgs/group_delete.html",
                {"group": group, "member_count": member_count, "error": error_msg},
            )

        group_name = group.name
        group.delete()
        messages.success(request, f"Group '{group_name}' deleted successfully.")
        return redirect("orgs:group_search")

    return render(
        request,
        "orgs/group_delete.html",
        {"group": group, "member_count": member_count},
    )

