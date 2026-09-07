from datetime import timedelta
import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from orgs.models import DepartmentGroup
from .models import ConfirmationToken, Role, User
from .services import confirm_account, issue_confirmation_token


@pytest.mark.django_db
class TestUC01RegistrationAndConfirmation:
    def test_register_creates_unconfirmed_user_and_token(self, client):
        response = client.post(
            reverse("accounts:register"),
            {
                "username": "newguest",
                "password": "ValidPassword123!",
                "email": "guest@vub.be",
                "first_name": "New",
                "last_name": "Guest",
                "university": "VUB",
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("accounts:confirm")

        user = User.objects.get(username="newguest")
        assert not user.is_confirmed
        assert user.role == Role.GUEST
        assert user.check_password("ValidPassword123!")

        token = ConfirmationToken.objects.filter(user=user).first()
        assert token is not None
        assert token.token
        assert token.attempts == 0
        assert len(mail.outbox) >= 1

    def test_register_missing_fields_fails(self, client):
        response = client.post(
            reverse("accounts:register"),
            {"username": "", "password": "", "email": "bademail"},
        )
        assert response.status_code == 200
        assert "Username is required." in response.content.decode()
        assert not User.objects.filter(username="").exists()

    def test_register_duplicate_username_fails(self, client):
        User.objects.create_user(username="existinguser", password="password", email="exist@vub.be")
        response = client.post(
            reverse("accounts:register"),
            {
                "username": "existinguser",
                "password": "newpassword",
                "email": "new@vub.be",
            },
        )
        assert response.status_code == 200
        assert "A user with that username already exists." in response.content.decode()

    def test_confirm_account_activates_member_and_deletes_token(self, client):
        user = User.objects.create_user(username="pending", password="pw", is_confirmed=False, role=Role.GUEST)
        token_str = issue_confirmation_token(user)

        response = client.post(reverse("accounts:confirm"), {"token": token_str})
        assert response.status_code == 302
        assert response.url == reverse("accounts:login")

        user.refresh_from_db()
        assert user.is_confirmed
        assert user.role == Role.MEMBER
        assert not ConfirmationToken.objects.filter(token=token_str).exists()

    def test_confirm_account_invalid_token_fails(self, client):
        response = client.post(reverse("accounts:confirm"), {"token": "completely-invalid-token"})
        assert response.status_code == 200
        assert "Invalid confirmation token." in response.content.decode()

    def test_confirm_account_expired_token_fails(self):
        user = User.objects.create_user(username="expired_user", password="pw", is_confirmed=False)
        token = ConfirmationToken.objects.create(
            user=user,
            token="expired-token-123",
            expires_at=timezone.now() - timedelta(hours=1),
        )
        success, msg = confirm_account("expired-token-123")
        assert not success
        assert "expired" in msg.lower()
        user.refresh_from_db()
        assert not user.is_confirmed

    def test_confirm_account_max_attempts_exceeded(self):
        user = User.objects.create_user(username="retry_user", password="pw", is_confirmed=False)
        ConfirmationToken.objects.create(
            user=user,
            token="valid-tok",
            expires_at=timezone.now() + timedelta(hours=24),
            attempts=5,
        )
        success, msg = confirm_account("valid-tok")
        assert not success
        assert "maximum" in msg.lower() or "exceeded" in msg.lower()


@pytest.mark.django_db
class TestUC02AuthenticationAndNetworkMode:
    def test_login_successful_for_confirmed_user(self, client):
        user = User.objects.create_user(
            username="confirmeduser",
            password="MySecretPassword",
            is_confirmed=True,
            role=Role.MEMBER,
        )
        response = client.post(
            reverse("accounts:login"),
            {"username": "confirmeduser", "password": "MySecretPassword"},
        )
        assert response.status_code == 302
        assert response.url == reverse("publications:search")

    def test_login_blocked_for_unconfirmed_user(self, client):
        User.objects.create_user(
            username="unconfirmeduser",
            password="MySecretPassword",
            is_confirmed=False,
            role=Role.GUEST,
        )
        response = client.post(
            reverse("accounts:login"),
            {"username": "unconfirmeduser", "password": "MySecretPassword"},
        )
        assert response.status_code == 200
        assert "confirmation is pending" in response.content.decode()

    def test_login_blocked_for_locked_user(self, client):
        User.objects.create_user(
            username="lockeduser",
            password="MySecretPassword",
            is_confirmed=True,
            is_locked=True,
            role=Role.MEMBER,
        )
        response = client.post(
            reverse("accounts:login"),
            {"username": "lockeduser", "password": "MySecretPassword"},
        )
        assert response.status_code == 200
        assert "account has been locked" in response.content.decode()

    def test_login_invalid_credentials_shows_generic_error(self, client):
        response = client.post(
            reverse("accounts:login"),
            {"username": "nonexistent", "password": "wrongpassword"},
        )
        assert response.status_code == 200

    def test_logout_redirects_to_login_in_internet_mode(self, client):
        user = User.objects.create_user(username="user1", password="pw", is_confirmed=True, role=Role.MEMBER)
        client.force_login(user)
        response = client.post(reverse("accounts:logout"))
        assert response.status_code == 302
        assert response.url == reverse("accounts:login")

    def test_logout_redirects_to_search_in_vub_network_mode(self, client):
        user = User.objects.create_user(username="user2", password="pw", is_confirmed=True, role=Role.MEMBER)
        client.force_login(user)
        session = client.session
        session["vub_network_mode"] = True
        session.save()

        response = client.post(reverse("accounts:logout"))
        assert response.status_code == 302
        assert response.url == reverse("publications:search")

    def test_network_mode_toggle(self, client):
        response = client.post(reverse("accounts:network_mode"), {"mode": "vub"})
        assert response.status_code == 302
        assert client.session["vub_network_mode"] is True

        response = client.post(reverse("accounts:network_mode"), {"mode": "internet"})
        assert response.status_code == 302
        assert client.session["vub_network_mode"] is False


@pytest.mark.django_db
class TestUC06UserAccountManagement:
    @pytest.fixture(autouse=True)
    def setup_users(self):
        self.dept_cs = DepartmentGroup.objects.create(name="Computer Science")
        self.dept_ee = DepartmentGroup.objects.create(name="Electrical Engineering")

        self.admin = User.objects.create_user(
            username="adminuser", password="pw", is_confirmed=True, role=Role.ADMINISTRATOR
        )
        self.mod_cs = User.objects.create_user(
            username="mod_cs", password="pw", is_confirmed=True, role=Role.MODERATOR, department=self.dept_cs
        )
        self.member_cs = User.objects.create_user(
            username="member_cs", password="pw", is_confirmed=True, role=Role.MEMBER, department=self.dept_cs
        )
        self.member_ee = User.objects.create_user(
            username="member_ee", password="pw", is_confirmed=True, role=Role.MEMBER, department=self.dept_ee
        )

    def test_admin_can_search_all_users(self, client):
        client.force_login(self.admin)
        response = client.get(reverse("accounts:user_search"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "member_cs" in content
        assert "member_ee" in content

    def test_moderator_search_is_restricted_to_own_department(self, client):
        client.force_login(self.mod_cs)
        response = client.get(reverse("accounts:user_search"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "member_cs" in content
        assert "member_ee" not in content

    def test_admin_can_create_user(self, client):
        client.force_login(self.admin)
        response = client.post(
            reverse("accounts:user_create"),
            {
                "username": "brandnewuser",
                "password": "Password123!",
                "email": "new@vub.be",
                "role": Role.PUBLISHER,
                "department": self.dept_cs.id,
            },
        )
        assert response.status_code == 302
        created = User.objects.get(username="brandnewuser")
        assert created.role == Role.PUBLISHER
        assert created.department == self.dept_cs

    def test_moderator_cannot_create_user(self, client):
        client.force_login(self.mod_cs)
        response = client.get(reverse("accounts:user_create"))
        assert response.status_code == 403

    def test_moderator_can_edit_user_in_own_department_to_publisher(self, client):
        client.force_login(self.mod_cs)
        response = client.post(
            reverse("accounts:user_edit", args=[self.member_cs.id]),
            {"first_name": "CS", "last_name": "Member", "email": "cs@vub.be", "role": Role.PUBLISHER},
        )
        assert response.status_code == 302
        self.member_cs.refresh_from_db()
        assert self.member_cs.role == Role.PUBLISHER

    def test_moderator_cannot_edit_user_outside_department(self, client):
        client.force_login(self.mod_cs)
        response = client.post(
            reverse("accounts:user_edit", args=[self.member_ee.id]),
            {"role": Role.PUBLISHER},
        )
        assert response.status_code == 403

    def test_moderator_cannot_grant_administrator_role(self, client):
        client.force_login(self.mod_cs)
        response = client.post(
            reverse("accounts:user_edit", args=[self.member_cs.id]),
            {"role": Role.ADMINISTRATOR},
        )
        assert response.status_code == 403
        self.member_cs.refresh_from_db()
        assert self.member_cs.role == Role.MEMBER

    def test_admin_can_delete_user(self, client):
        client.force_login(self.admin)
        response = client.post(reverse("accounts:user_delete", args=[self.member_ee.id]))
        assert response.status_code == 302
        assert not User.objects.filter(id=self.member_ee.id).exists()

    def test_moderator_cannot_delete_user(self, client):
        client.force_login(self.mod_cs)
        response = client.post(reverse("accounts:user_delete", args=[self.member_cs.id]))
        assert response.status_code == 403

