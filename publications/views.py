import os
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import Role
from accounts.permissions import require_role
from .models import Publication
from .services import bundle_publications_zip, extract_bibliographic_metadata, search_publications


@require_role("vub_network", "member", "publisher", "moderator", "administrator")
@require_http_methods(["GET"])
def search(request):
    criteria = {
        "keywords": request.GET.get("keywords", "").strip(),
        "authors": request.GET.get("authors", "").strip(),
        "date_from": request.GET.get("date_from", "").strip(),
        "date_to": request.GET.get("date_to", "").strip(),
        "ordering": request.GET.get("ordering", ""),
    }
    has_searched = any(criteria.values())
    qs = search_publications(criteria)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Check if user has permission to edit each publication
    can_manage = False
    if request.user.is_authenticated and request.user.role in [
        Role.PUBLISHER,
        Role.MODERATOR,
        Role.ADMINISTRATOR,
    ]:
        can_manage = True

    return render(
        request,
        "publications/search.html",
        {
            "page_obj": page_obj,
            "criteria": criteria,
            "has_searched": has_searched,
            "can_manage": can_manage,
            "total_count": paginator.count,
        },
    )


@require_role("vub_network", "member", "publisher", "moderator", "administrator")
@require_http_methods(["GET"])
def download(request, pk):
    pub = get_object_or_404(Publication, pk=pk)
    if not pub.file:
        return render(
            request,
            "publications/download.html",
            {
                "publication": pub,
                "is_abstract_only": True,
                "message": "Full text is not available for this publication (abstract only).",
            },
        )

    try:
        f = pub.file.open("rb")
        filename = os.path.basename(pub.file.name)
        return FileResponse(f, as_attachment=True, filename=filename)
    except Exception:
        return render(
            request,
            "publications/download.html",
            {
                "publication": pub,
                "error": "File storage temporarily unreachable. Please contact the administrator.",
            },
        )


@require_role("vub_network", "member", "publisher", "moderator", "administrator")
@require_http_methods(["GET", "POST"])
def download_all(request):
    pids = request.GET.getlist("pids") or request.POST.getlist("pids")
    if pids:
        pubs = Publication.objects.filter(id__in=pids)
    else:
        # If no specific IDs, bundle matching search criteria or all
        criteria = {
            "keywords": request.GET.get("keywords", "").strip(),
            "authors": request.GET.get("authors", "").strip(),
            "date_from": request.GET.get("date_from", "").strip(),
            "date_to": request.GET.get("date_to", "").strip(),
        }
        pubs = search_publications(criteria)

    if not pubs.exists():
        messages.warning(request, "No publications found to download.")
        return redirect("publications:search")

    zip_buffer = bundle_publications_zip(pubs)
    return FileResponse(
        zip_buffer,
        as_attachment=True,
        filename="publications_archive.zip",
        content_type="application/zip",
    )


@require_role("publisher", "moderator", "administrator")
@require_http_methods(["GET", "POST"])
def upload(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("document")
        meta = {}
        if uploaded_file:
            meta = extract_bibliographic_metadata(uploaded_file)

        title = request.POST.get("title", "").strip() or meta.get("title")
        authors = request.POST.get("authors", "").strip() or meta.get("authors")
        year_val = request.POST.get("year", "").strip() or meta.get("year")
        abstract = request.POST.get("abstract", "").strip() or meta.get("abstract", "")

        year = None
        if year_val:
            try:
                year = int(year_val)
            except (ValueError, TypeError):
                pass

        if not title:
            title = getattr(uploaded_file, "name", "Untitled Publication")
        if not authors:
            authors = request.user.get_full_name() or request.user.username

        pub = Publication.objects.create(
            title=title,
            authors=authors,
            year=year,
            abstract=abstract,
            owner=request.user,
            file=uploaded_file or "",
        )
        messages.success(request, f"Publication '{pub.title}' uploaded successfully.")
        return redirect("publications:mine")

    return render(request, "publications/upload.html")


@require_role("publisher", "moderator", "administrator")
@require_http_methods(["GET"])
def mine(request):
    publications = Publication.objects.filter(owner=request.user).order_by("-uploaded_at")
    return render(request, "publications/mine.html", {"publications": publications})


@require_role("publisher", "moderator", "administrator")
@require_http_methods(["GET", "POST"])
def edit(request, pk):
    pub = get_object_or_404(Publication, pk=pk)

    # Ownership check: Publishers can only edit publications they own.
    # Moderators and Administrators inherit permission to edit any publication.
    if request.user.role == Role.PUBLISHER and pub.owner_id != request.user.id:
        return HttpResponseForbidden("You do not have permission to edit publications you do not own.")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        authors = request.POST.get("authors", "").strip()
        year_str = request.POST.get("year", "").strip()
        abstract = request.POST.get("abstract", "").strip()

        if title:
            pub.title = title
        if authors:
            pub.authors = authors
        if year_str.isdigit():
            pub.year = int(year_str)
        elif not year_str:
            pub.year = None
        pub.abstract = abstract

        if "file" in request.FILES:
            pub.file = request.FILES["file"]

        pub.save()
        messages.success(request, f"Publication '{pub.title}' updated successfully.")
        return redirect("publications:mine")

    return render(request, "publications/edit.html", {"publication": pub})

