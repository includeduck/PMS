from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from accounts.permissions import require_role


@require_role("vub_network", "member", "publisher", "moderator", "administrator")
@require_http_methods(["GET", "POST"])
def search(request):
    return render(request, "publications/search.html")


@require_role("vub_network", "member", "publisher", "moderator", "administrator")
@require_http_methods(["GET", "POST"])
def download(request, pk):
    return render(request, "publications/download.html", {"publication_id": pk})


@require_role("vub_network", "member", "publisher", "moderator", "administrator")
@require_http_methods(["GET", "POST"])
def download_all(request):
    return render(request, "publications/download_all.html")


@require_role("publisher", "moderator", "administrator")
@require_http_methods(["GET", "POST"])
def upload(request):
    return render(request, "publications/upload.html")


@require_role("publisher", "moderator", "administrator")
@require_http_methods(["GET"])
def mine(request):
    return render(request, "publications/mine.html")


@require_role("publisher", "moderator", "administrator")
@require_http_methods(["GET", "POST"])
def edit(request, pk):
    return render(request, "publications/edit.html", {"publication_id": pk})
