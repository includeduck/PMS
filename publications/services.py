"""Publication search, download, and metadata extraction (UC-03–UC-05)."""

import io
import os
import re
import zipfile
from django.db.models import Q
from .models import Publication


def search_publications(criteria=None):
    """
    Search publications matching the specified criteria.
    criteria keys:
      - keywords: string (matches title or abstract)
      - authors: string (matches authors)
      - date_from: int/string (year >= date_from)
      - date_to: int/string (year <= date_to)
      - ordering: string (e.g. title, -title, year, -year, authors, -authors)
    """
    criteria = criteria or {}
    qs = Publication.objects.select_related("owner").all()

    keywords = (criteria.get("keywords") or "").strip()
    if keywords:
        qs = qs.filter(Q(title__icontains=keywords) | Q(abstract__icontains=keywords))

    authors = (criteria.get("authors") or "").strip()
    if authors:
        qs = qs.filter(authors__icontains=authors)

    date_from = str(criteria.get("date_from") or "").strip()
    if date_from.isdigit():
        qs = qs.filter(year__gte=int(date_from))

    date_to = str(criteria.get("date_to") or "").strip()
    if date_to.isdigit():
        qs = qs.filter(year__lte=int(date_to))

    ordering = criteria.get("ordering")
    valid_orderings = {
        "title": "title",
        "-title": "-title",
        "authors": "authors",
        "-authors": "-authors",
        "year": "year",
        "-year": "-year",
    }
    if ordering in valid_orderings:
        qs = qs.order_by(valid_orderings[ordering])
    else:
        qs = qs.order_by("-year", "title")

    return qs


def bundle_publications_zip(publications):
    """
    Package an iterable of Publication instances into an in-memory zip archive.
    Returns io.BytesIO buffer positioned at start.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for pub in publications:
            has_file = False
            if pub.file:
                try:
                    pub.file.open("rb")
                    content = pub.file.read()
                    pub.file.close()
                    filename = f"pub_{pub.id}_{os.path.basename(pub.file.name)}"
                    zf.writestr(filename, content)
                    has_file = True
                except Exception:
                    pass

            if not has_file:
                # Abstract-only or missing file record
                meta_content = (
                    f"Title: {pub.title}\n"
                    f"Authors: {pub.authors}\n"
                    f"Year: {pub.year or 'N/A'}\n"
                    f"Owner: {pub.owner.username}\n\n"
                    f"Abstract:\n{pub.abstract or '(No abstract available)'}\n"
                )
                zf.writestr(f"pub_{pub.id}_abstract_only.txt", meta_content)

    buffer.seek(0)
    return buffer


def extract_bibliographic_metadata(uploaded_file):
    """
    Extract title, authors, year, and abstract from an uploaded document (pdf, ps, bib, ris, txt).
    Returns a dict with extracted strings.
    """
    metadata = {
        "title": "",
        "authors": "",
        "year": None,
        "abstract": "",
    }
    filename = getattr(uploaded_file, "name", "").lower()

    # Default title to filename stem
    base_title = os.path.splitext(os.path.basename(getattr(uploaded_file, "name", "Publication")))[0]
    metadata["title"] = base_title.replace("_", " ").replace("-", " ").title()

    try:
        content_bytes = uploaded_file.read()
        uploaded_file.seek(0)
    except Exception:
        return metadata

    # 1. BibTeX parsing
    if filename.endswith(".bib") or b"@" in content_bytes and b"{" in content_bytes:
        try:
            text = content_bytes.decode("utf-8", errors="ignore")
            title_m = re.search(r'title\s*=\s*[\{"]([^"\}]+)[\}"]', text, re.IGNORECASE)
            if title_m:
                metadata["title"] = title_m.group(1).strip()
            author_m = re.search(r'author\s*=\s*[\{"]([^"\}]+)[\}"]', text, re.IGNORECASE)
            if author_m:
                metadata["authors"] = author_m.group(1).strip()
            year_m = re.search(r'year\s*=\s*[\{"]?(\d{4})[\}"]?', text, re.IGNORECASE)
            if year_m:
                metadata["year"] = int(year_m.group(1))
            abstract_m = re.search(r'abstract\s*=\s*[\{"]([^"\}]+)[\}"]', text, re.IGNORECASE)
            if abstract_m:
                metadata["abstract"] = abstract_m.group(1).strip()
            return metadata
        except Exception:
            pass

    # 2. RIS parsing
    if filename.endswith(".ris") or b"TY  - " in content_bytes:
        try:
            text = content_bytes.decode("utf-8", errors="ignore")
            title_m = re.search(r"^(?:TI|T1)\s*-\s*(.+)$", text, re.MULTILINE)
            if title_m:
                metadata["title"] = title_m.group(1).strip()
            authors = re.findall(r"^(?:AU|A1)\s*-\s*(.+)$", text, re.MULTILINE)
            if authors:
                metadata["authors"] = ", ".join(a.strip() for a in authors)
            year_m = re.search(r"^(?:PY|Y1)\s*-\s*(\d{4})", text, re.MULTILINE)
            if year_m:
                metadata["year"] = int(year_m.group(1))
            abstract_m = re.search(r"^(?:AB|N2)\s*-\s*(.+)$", text, re.MULTILINE)
            if abstract_m:
                metadata["abstract"] = abstract_m.group(1).strip()
            return metadata
        except Exception:
            pass

    # 3. PDF parsing via pypdf
    if filename.endswith(".pdf"):
        try:
            import pypdf

            stream = io.BytesIO(content_bytes)
            reader = pypdf.PdfReader(stream)
            doc_info = reader.metadata
            if doc_info:
                if doc_info.title:
                    metadata["title"] = str(doc_info.title).strip()
                if doc_info.author:
                    metadata["authors"] = str(doc_info.author).strip()
                if doc_info.creation_date:
                    try:
                        metadata["year"] = doc_info.creation_date.year
                    except Exception:
                        pass

            # Extract first page text for fallback title/abstract if metadata was sparse
            if len(reader.pages) > 0:
                first_page = reader.pages[0].extract_text() or ""
                lines = [l.strip() for l in first_page.splitlines() if l.strip()]
                if not metadata["title"] and lines:
                    metadata["title"] = lines[0]
                if not metadata["abstract"]:
                    ab_idx = -1
                    for idx, line in enumerate(lines):
                        if "abstract" in line.lower():
                            ab_idx = idx
                            break
                    if ab_idx != -1 and ab_idx + 1 < len(lines):
                        metadata["abstract"] = " ".join(lines[ab_idx + 1 : ab_idx + 6])
        except Exception:
            pass

    return metadata

