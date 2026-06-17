from django.contrib.auth import get_user_model
from users_app.utils import send_activation_email, send_password_reset_email


def task_send_activation_email(user_id):
    """Fetches the user by ID and sends the account activation email.
    Runs as an RQ background job on the high queue."""
    user = get_user_model().objects.get(pk=user_id)
    send_activation_email(user)


def task_send_password_reset_email(user_id):
    """Fetches the user by ID and sends the password reset email.
    Runs as an RQ background job on the high queue."""
    user = get_user_model().objects.get(pk=user_id)
    send_password_reset_email(user)
