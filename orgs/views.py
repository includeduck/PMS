from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from accounts.permissions import require_role


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def group_search(request):
    return render(request, "orgs/group_search.html")


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def group_create(request):
    return render(request, "orgs/group_create.html")


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def group_edit(request, pk):
    return render(request, "orgs/group_edit.html", {"group_id": pk})


@require_role("administrator")
@require_http_methods(["GET", "POST"])
def group_delete(request, pk):
    return render(request, "orgs/group_delete.html", {"group_id": pk})
