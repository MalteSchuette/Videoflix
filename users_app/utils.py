from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from users_app.email_templates import (
    get_activation_email_html, get_password_reset_email_html,
)


def set_auth_cookies(response, access_token, refresh_token):
    """Sets access_token and refresh_token as HttpOnly cookies on the
    response."""
    response.set_cookie(
        'access_token', str(access_token), httponly=True, samesite='Lax'
    )
    response.set_cookie(
        'refresh_token', str(refresh_token), httponly=True, samesite='Lax'
    )


def delete_auth_cookies(response):
    """Deletes the JWT auth cookies from the response."""
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


def generate_uid_token(user):
    """Generates a base64-encoded user ID and a signed token for use
    in email links."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def send_activation_email(user):
    uid, token = generate_uid_token(user)
    activation_link = (
        f"{settings.FRONTEND_URL}/pages/auth/activate.html"
        f"?uid={uid}&token={token}"
    )
    html = get_activation_email_html(
        username=user.username, activation_url=activation_link
    )
    email = EmailMultiAlternatives(
        subject='Confirm your email',
        body=f'Please activate your account: {activation_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html, 'text/html')
    email.send()


def send_password_reset_email(user):
    uid, token = generate_uid_token(user)
    reset_link = (
        f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html"
        f"?uid={uid}&token={token}"
    )
    html = get_password_reset_email_html(reset_url=reset_link)
    email = EmailMultiAlternatives(
        subject='Reset your Password',
        body=f'Reset your password: {reset_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html, 'text/html')
    email.send()
