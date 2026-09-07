"""Account confirmation helpers (UC-01)."""

import secrets
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import ConfirmationToken, Role


def issue_confirmation_token(user):
    """
    Generate and persist a confirmation token for the user, and notify the user and admin via console email.
    """
    token_str = secrets.token_urlsafe(16)
    expires_at = timezone.now() + timedelta(hours=24)
    token = ConfirmationToken.objects.create(
        user=user,
        token=token_str,
        expires_at=expires_at,
        attempts=0,
    )

    # Notify via email (console backend in dev)
    subject = "PMS Account Confirmation Token"
    message = (
        f"Hello {user.first_name or user.username},\n\n"
        f"Your PMS account has been created. Use the following token to confirm your account:\n\n"
        f"{token_str}\n\n"
        f"This token expires in 24 hours.\n"
    )
    admin_subject = f"PMS: New Account Pending Confirmation ({user.username})"
    admin_message = f"User {user.username} ({user.email}) registered and is awaiting confirmation."

    try:
        if user.email:
            send_mail(
                subject,
                message,
                getattr(settings, "DEFAULT_FROM_EMAIL", "admin@pms.local"),
                [user.email],
                fail_silently=True,
            )
        send_mail(
            admin_subject,
            admin_message,
            getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@pms.local"),
            ["admin@pms.local"],
            fail_silently=True,
        )
    except Exception:
        pass

    return token_str


def confirm_account(token_str, user=None):
    """
    Confirm an account using a token string.
    Returns (success: bool, message: str).
    """
    token_str = (token_str or "").strip()
    if not token_str:
        return False, "Please enter a confirmation token."

    if user:
        token_obj = ConfirmationToken.objects.filter(user=user).order_by("-created_at").first()
        if not token_obj:
            return False, "No active confirmation token found for this account."
        if token_obj.attempts >= 5:
            return False, "Maximum confirmation attempts exceeded for this token."
        if timezone.now() > token_obj.expires_at:
            return False, "Confirmation token has expired."
        if token_obj.token != token_str:
            token_obj.attempts += 1
            token_obj.save(update_fields=["attempts"])
            remaining = max(0, 5 - token_obj.attempts)
            return False, f"Invalid token. {remaining} attempt(s) remaining."
    else:
        token_obj = ConfirmationToken.objects.filter(token=token_str).select_related("user").first()
        if not token_obj:
            return False, "Invalid confirmation token."
        if token_obj.attempts >= 5:
            return False, "Maximum confirmation attempts exceeded for this token."
        if timezone.now() > token_obj.expires_at:
            return False, "Confirmation token has expired."

    target_user = user or token_obj.user
    target_user.is_confirmed = True
    target_user.role = Role.MEMBER
    target_user.save(update_fields=["is_confirmed", "role"])
    token_obj.delete()

    return True, "Account successfully confirmed at Member level."

