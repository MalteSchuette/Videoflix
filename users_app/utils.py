from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def generate_uid_token(user):
    """Generates a base64-encoded user ID and a signed token for use in email links."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def send_activation_email(user):
    """Sends an account activation email containing a link to activate the user's account."""
    uid, token = generate_uid_token(user)
    activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"
    send_mail(
        subject='Activate your Videoflix account',
        message=f'Please activate your account: {activation_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_password_reset_email(user):
    """Sends a password reset email containing a link to set a new password."""
    uid, token = generate_uid_token(user)
    reset_link = f"{settings.FRONTEND_URL}/password-reset/{uid}/{token}/"
    send_mail(
        subject='Reset your Videoflix password',
        message=f'Reset your password: {reset_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
