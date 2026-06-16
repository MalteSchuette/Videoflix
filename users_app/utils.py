from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def set_auth_cookies(response, access_token, refresh_token):
    """Sets access_token and refresh_token as HttpOnly cookies on the response."""
    response.set_cookie('access_token', str(access_token), httponly=True, samesite='Lax')
    response.set_cookie('refresh_token', str(refresh_token), httponly=True, samesite='Lax')


def delete_auth_cookies(response):
    """Deletes the JWT auth cookies from the response."""
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


def generate_uid_token(user):
    """Generates a base64-encoded user ID and a signed token for use in email links."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def build_email_html(heading, body_text, button_label, button_url):
    """Returns a styled HTML email string with a centered card, heading, body text, and CTA button."""
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background-color:#141414;font-family:Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#141414;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="520" cellpadding="0" cellspacing="0" style="background-color:#1f1f1f;border-radius:8px;overflow:hidden;">
              <tr>
                <td style="background-color:#e50914;padding:24px 40px;">
                  <p style="margin:0;color:#ffffff;font-size:26px;font-weight:bold;letter-spacing:2px;">VIDEOFLIX</p>
                </td>
              </tr>
              <tr>
                <td style="padding:40px;">
                  <h1 style="margin:0 0 16px;color:#ffffff;font-size:22px;">{heading}</h1>
                  <p style="margin:0 0 32px;color:#b3b3b3;font-size:15px;line-height:1.6;">{body_text}</p>
                  <a href="{button_url}"
                     style="display:inline-block;background-color:#e50914;color:#ffffff;text-decoration:none;
                            font-size:15px;font-weight:bold;padding:14px 32px;border-radius:4px;">
                    {button_label}
                  </a>
                  <p style="margin:32px 0 0;color:#555555;font-size:12px;">
                    Falls der Button nicht funktioniert, kopiere diesen Link in deinen Browser:<br>
                    <a href="{button_url}" style="color:#e50914;word-break:break-all;">{button_url}</a>
                  </p>
                </td>
              </tr>
              <tr>
                <td style="padding:20px 40px;border-top:1px solid #2a2a2a;">
                  <p style="margin:0;color:#555555;font-size:12px;">
                    Du hast diese E-Mail erhalten, weil deine Adresse bei Videoflix verwendet wurde.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


def send_activation_email(user):
    """Sends an HTML account activation email with a link to activate the user's account."""
    uid, token = generate_uid_token(user)
    activation_link = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uid}&token={token}"
    html = build_email_html(
        heading='Konto aktivieren',
        body_text='Willkommen bei Videoflix! Klicke auf den Button, um dein Konto zu aktivieren und loszulegen.',
        button_label='Konto jetzt aktivieren',
        button_url=activation_link,
    )
    email = EmailMultiAlternatives(
        subject='Aktiviere dein Videoflix-Konto',
        body=f'Bitte aktiviere dein Konto: {activation_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html, 'text/html')
    email.send()


def send_password_reset_email(user):
    """Sends an HTML password reset email with a link to set a new password."""
    uid, token = generate_uid_token(user)
    reset_link = f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uid}&token={token}"
    html = build_email_html(
        heading='Passwort zurücksetzen',
        body_text='Du hast eine Anfrage zum Zurücksetzen deines Passworts gestellt. Klicke auf den Button, um ein neues Passwort zu vergeben.',
        button_label='Passwort jetzt zurücksetzen',
        button_url=reset_link,
    )
    email = EmailMultiAlternatives(
        subject='Passwort zurücksetzen – Videoflix',
        body=f'Passwort zurücksetzen: {reset_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html, 'text/html')
    email.send()
