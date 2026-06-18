import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

_LOGO_PATH = os.path.join(
    os.path.dirname(__file__),
    "static", "users_app", "images", "Logo.png"
)
with open(_LOGO_PATH, "rb") as _f:
    _LOGO_DATA = _f.read()


def _send_html_email(subject, html, to):
    """Sends an HTML email with an inline logo using multipart/related."""
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = settings.DEFAULT_FROM_EMAIL
    msg["To"] = to

    msg.attach(MIMEText(html, "html", "utf-8"))

    logo = MIMEImage(_LOGO_DATA)
    logo.add_header("Content-ID", "<logo>")
    logo.add_header("Content-Disposition", "inline", filename="Logo.png")
    msg.attach(logo)

    connection = get_connection()
    connection.open()
    connection.connection.sendmail(
        settings.DEFAULT_FROM_EMAIL, [to], msg.as_string()
    )
    connection.close()


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
    html = render_to_string("activation_email.html", {
        "username": user.email,
        "activation_url": activation_link,
    })
    _send_html_email(
        subject='Confirm your email',
        html=html,
        to=user.email,
    )


def send_password_reset_email(user):
    uid, token = generate_uid_token(user)
    reset_link = (
        f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html"
        f"?uid={uid}&token={token}"
    )
    html = render_to_string("password_reset_email.html", {
        "reset_url": reset_link,
    })
    _send_html_email(
        subject='Reset your Password',
        html=html,
        to=user.email,
    )
