import pytest
from django.urls import reverse

from accounts.models import Role, User
from .models import DepartmentGroup


@pytest.mark.django_db
class TestUC07GroupManagement:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.admin = User.objects.create_user(
            username="adminuser", password="pw", is_confirmed=True, role=Role.ADMINISTRATOR
        )
        self.member = User.objects.create_user(
            username="memberuser", password="pw", is_confirmed=True, role=Role.MEMBER
        )

    def test_admin_can_create_group(self, client):
        client.force_login(self.admin)
        response = client.post(
            reverse("orgs:group_create"),
            {"name": "Physics Department", "description": "Study of matter and energy"},
        )
        assert response.status_code == 302
        assert DepartmentGroup.objects.filter(name="Physics Department").exists()

    def test_create_duplicate_group_name_fails(self, client):
        DepartmentGroup.objects.create(name="Biology")
        client.force_login(self.admin)
        response = client.post(
            reverse("orgs:group_create"),
            {"name": "Biology", "description": "Duplicate group"},
        )
        assert response.status_code == 200
        assert "A group with this name already exists." in response.content.decode()

    def test_admin_can_edit_group_and_membership(self, client):
        group = DepartmentGroup.objects.create(name="Math")
        client.force_login(self.admin)
        response = client.post(
            reverse("orgs:group_edit", args=[group.id]),
            {"name": "Mathematics", "description": "Pure and applied", "users": [self.member.id]},
        )
        assert response.status_code == 302
        group.refresh_from_db()
        assert group.name == "Mathematics"
        self.member.refresh_from_db()
        assert self.member.department == group

    def test_admin_can_delete_empty_group(self, client):
        group = DepartmentGroup.objects.create(name="Temporary Group")
        client.force_login(self.admin)
        response = client.post(reverse("orgs:group_delete", args=[group.id]))
        assert response.status_code == 302
        assert not DepartmentGroup.objects.filter(id=group.id).exists()

    def test_admin_cannot_delete_non_empty_group_live_check(self, client):
        group = DepartmentGroup.objects.create(name="Active Department")
        self.member.department = group
        self.member.save()

        client.force_login(self.admin)
        response = client.post(reverse("orgs:group_delete", args=[group.id]))
        assert response.status_code == 200
        assert "Cannot delete group: group still has members" in response.content.decode()
        assert DepartmentGroup.objects.filter(id=group.id).exists()

    def test_non_admin_cannot_manage_groups(self, client):
        client.force_login(self.member)
        response = client.get(reverse("orgs:group_search"))
        assert response.status_code == 403

        response = client.get(reverse("orgs:group_create"))
        assert response.status_code == 403

