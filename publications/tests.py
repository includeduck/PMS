import io
import zipfile
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from accounts.models import Role, User
from .models import Publication


@pytest.mark.django_db
class TestUC03SearchPublications:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.user = User.objects.create_user(
            username="pubuser", password="pw", is_confirmed=True, role=Role.PUBLISHER
        )
        self.pub1 = Publication.objects.create(
            title="Software Testing in Practice",
            authors="Alice Smith, Bob Jones",
            year=2021,
            abstract="A comprehensive study of test-driven development.",
            owner=self.user,
        )
        self.pub2 = Publication.objects.create(
            title="Quality Assurance in Agile",
            authors="Charlie Brown",
            year=2024,
            abstract="Agile QA principles and CI/CD pipelines.",
            owner=self.user,
        )

    def test_guest_cannot_search_without_vub_network_mode(self, client):
        response = client.get(reverse("publications:search"))
        # Unauthenticated guest is redirected to login
        assert response.status_code == 302
        assert reverse("accounts:login") in response.url

    def test_vub_network_user_can_search_without_account(self, client):
        session = client.session
        session["vub_network_mode"] = True
        session.save()

        response = client.get(reverse("publications:search"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Software Testing in Practice" in content
        assert "Quality Assurance in Agile" in content

    def test_member_can_search(self, client):
        client.force_login(self.user)
        response = client.get(reverse("publications:search"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Software Testing in Practice" in content

    def test_search_by_keywords(self, client):
        client.force_login(self.user)
        response = client.get(reverse("publications:search"), {"keywords": "Agile"})
        assert response.status_code == 200
        content = response.content.decode()
        assert "Quality Assurance in Agile" in content
        assert "Software Testing in Practice" not in content

    def test_search_by_authors(self, client):
        client.force_login(self.user)
        response = client.get(reverse("publications:search"), {"authors": "Alice"})
        assert response.status_code == 200
        content = response.content.decode()
        assert "Software Testing in Practice" in content
        assert "Quality Assurance in Agile" not in content

    def test_search_by_date_range(self, client):
        client.force_login(self.user)
        response = client.get(reverse("publications:search"), {"date_from": "2023", "date_to": "2025"})
        assert response.status_code == 200
        content = response.content.decode()
        assert "Quality Assurance in Agile" in content
        assert "Software Testing in Practice" not in content

    def test_search_no_results_shows_message(self, client):
        client.force_login(self.user)
        response = client.get(reverse("publications:search"), {"keywords": "Quantum Computing 999"})
        assert response.status_code == 200
        assert "No publications match your search criteria" in response.content.decode()


@pytest.mark.django_db
class TestUC04DownloadPublications:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.user = User.objects.create_user(
            username="pubuser", password="pw", is_confirmed=True, role=Role.PUBLISHER
        )
        fake_pdf = SimpleUploadedFile("sample.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        self.pub_with_file = Publication.objects.create(
            title="Publication With File",
            authors="Author One",
            year=2023,
            file=fake_pdf,
            owner=self.user,
        )
        self.pub_abstract_only = Publication.objects.create(
            title="Publication Abstract Only",
            authors="Author Two",
            year=2022,
            abstract="Only the abstract is available for this record.",
            owner=self.user,
        )

    def test_single_file_download_streams_content(self, client):
        client.force_login(self.user)
        response = client.get(reverse("publications:download", args=[self.pub_with_file.id]))
        assert response.status_code == 200
        assert b"%PDF-1.4 sample content" in response.getvalue()

    def test_abstract_only_download_shows_notice(self, client):
        client.force_login(self.user)
        response = client.get(reverse("publications:download", args=[self.pub_abstract_only.id]))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Full text is not available for this publication" in content

    def test_bulk_download_produces_valid_zip(self, client):
        client.force_login(self.user)
        response = client.get(
            reverse("publications:download_all"),
            {"pids": [self.pub_with_file.id, self.pub_abstract_only.id]},
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "application/zip"

        # Verify zip archive content
        zip_bytes = io.BytesIO(response.getvalue())
        with zipfile.ZipFile(zip_bytes, "r") as zf:
            namelist = zf.namelist()
            assert any(f"pub_{self.pub_with_file.id}_" in name for name in namelist)
            assert any(f"pub_{self.pub_abstract_only.id}_" in name for name in namelist)


@pytest.mark.django_db
class TestUC05ManageOwnPublications:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.publisher1 = User.objects.create_user(
            username="publisher1", password="pw", is_confirmed=True, role=Role.PUBLISHER
        )
        self.publisher2 = User.objects.create_user(
            username="publisher2", password="pw", is_confirmed=True, role=Role.PUBLISHER
        )
        self.moderator = User.objects.create_user(
            username="moderator", password="pw", is_confirmed=True, role=Role.MODERATOR
        )
        self.member = User.objects.create_user(
            username="member", password="pw", is_confirmed=True, role=Role.MEMBER
        )

        self.pub1 = Publication.objects.create(
            title="Publisher 1 Paper",
            authors="Publisher One",
            year=2022,
            owner=self.publisher1,
        )

    def test_member_cannot_upload_publications(self, client):
        client.force_login(self.member)
        response = client.get(reverse("publications:upload"))
        assert response.status_code == 403

    def test_publisher_can_upload_publication(self, client):
        client.force_login(self.publisher1)
        bib_content = b"""
        @article{smith2025,
          title={BibTeX Test Paper},
          author={John Smith and Jane Doe},
          year={2025},
          abstract={A test abstract extracted from BibTeX.}
        }
        """
        uploaded = SimpleUploadedFile("paper.bib", bib_content, content_type="text/plain")
        response = client.post(reverse("publications:upload"), {"document": uploaded})
        assert response.status_code == 302
        assert response.url == reverse("publications:mine")

        created = Publication.objects.get(title="BibTeX Test Paper")
        assert created.owner == self.publisher1
        assert created.authors == "John Smith and Jane Doe"
        assert created.year == 2025
        assert "extracted from BibTeX" in created.abstract

    def test_publisher_my_publications_shows_only_owned(self, client):
        Publication.objects.create(
            title="Publisher 2 Paper",
            authors="Publisher Two",
            owner=self.publisher2,
        )
        client.force_login(self.publisher1)
        response = client.get(reverse("publications:mine"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Publisher 1 Paper" in content
        assert "Publisher 2 Paper" not in content

    def test_publisher_can_edit_own_publication(self, client):
        client.force_login(self.publisher1)
        response = client.post(
            reverse("publications:edit", args=[self.pub1.id]),
            {
                "title": "Updated Paper Title",
                "authors": "Publisher One Updated",
                "year": "2026",
                "abstract": "Updated abstract content.",
            },
        )
        assert response.status_code == 302
        self.pub1.refresh_from_db()
        assert self.pub1.title == "Updated Paper Title"
        assert self.pub1.year == 2026

    def test_publisher_cannot_edit_others_publication(self, client):
        client.force_login(self.publisher2)
        response = client.post(
            reverse("publications:edit", args=[self.pub1.id]),
            {"title": "Hacked Title"},
        )
        assert response.status_code == 403
        self.pub1.refresh_from_db()
        assert self.pub1.title == "Publisher 1 Paper"

    def test_moderator_can_edit_any_publication(self, client):
        client.force_login(self.moderator)
        response = client.post(
            reverse("publications:edit", args=[self.pub1.id]),
            {
                "title": "Moderator Edited Title",
                "authors": self.pub1.authors,
            },
        )
        assert response.status_code == 302
        self.pub1.refresh_from_db()
        assert self.pub1.title == "Moderator Edited Title"

