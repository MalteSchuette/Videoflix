from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def make_uid_token(user):
    """Generates a base64-encoded UID and signed token for the given user,
    used to build activation and reset links in tests."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def create_active_user(email='test@example.com', password='Test1234!'):
    """Creates and returns an active test user with the given email
    and password."""
    return User.objects.create_user(
        email=email, password=password, is_active=True
    )


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class RegisterViewTests(APITestCase):
    """Tests for the user registration endpoint."""

    def test_register_success(self):
        """Checks that a valid registration returns 201 and creates an
        inactive user."""
        response = self.client.post('/api/register/', {
            'email': 'new@example.com',
            'password': 'Test1234!',
            'confirmed_password': 'Test1234!',
        })
        self.assertEqual(response.status_code, 201)
        self.assertFalse(User.objects.get(email='new@example.com').is_active)

    def test_register_password_mismatch(self):
        """Checks that mismatched passwords return 400."""
        response = self.client.post('/api/register/', {
            'email': 'new@example.com',
            'password': 'Test1234!',
            'confirmed_password': 'Wrong1234!',
        })
        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_email(self):
        """Checks that registering with an already existing email
        returns 400."""
        create_active_user(email='dup@example.com')
        response = self.client.post('/api/register/', {
            'email': 'dup@example.com',
            'password': 'Test1234!',
            'confirmed_password': 'Test1234!',
        })
        self.assertEqual(response.status_code, 400)


class ActivateViewTests(APITestCase):
    """Tests for the account activation endpoint."""

    def test_activate_success(self):
        """Checks that a valid UID and token activate the user account."""
        user = User.objects.create_user(
            email='inactive@example.com', password='Test1234!'
        )
        uid, token = make_uid_token(user)
        response = self.client.get(f'/api/activate/{uid}/{token}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.get(pk=user.pk).is_active)

    def test_activate_invalid_token(self):
        """Checks that an invalid token returns 400."""
        user = User.objects.create_user(
            email='inactive2@example.com', password='Test1234!'
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        response = self.client.get(f'/api/activate/{uid}/invalidtoken/')
        self.assertEqual(response.status_code, 400)

    def test_activate_invalid_uid(self):
        """Checks that a malformed UID returns 400."""
        response = self.client.get('/api/activate/invaliduid/sometoken/')
        self.assertEqual(response.status_code, 400)


class LoginViewTests(APITestCase):
    """Tests for the login endpoint."""

    def setUp(self):
        """Creates an active user for login tests."""
        self.user = create_active_user()

    def test_login_success(self):
        """Checks that valid credentials return 200 and set JWT cookies."""
        response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'Test1234!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_login_wrong_password(self):
        """Checks that a wrong password returns 400."""
        response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'WrongPass!',
        })
        self.assertEqual(response.status_code, 400)

    def test_login_inactive_user(self):
        """Checks that an inactive user cannot log in."""
        User.objects.create_user(
            email='inactive@example.com', password='Test1234!'
        )
        response = self.client.post('/api/login/', {
            'email': 'inactive@example.com',
            'password': 'Test1234!',
        })
        self.assertEqual(response.status_code, 400)


class LogoutViewTests(APITestCase):
    """Tests for the logout endpoint."""

    def setUp(self):
        """Creates an active user and sets JWT cookies for logout tests."""
        self.user = create_active_user()
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['access_token'] = str(refresh.access_token)
        self.client.cookies['refresh_token'] = str(refresh)

    def test_logout_success(self):
        """Checks that a logout with a valid refresh cookie returns 200."""
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 200)

    def test_logout_without_cookie(self):
        """Checks that a logout without a refresh cookie returns 400."""
        self.client.cookies.clear()
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 400)


class TokenRefreshViewTests(APITestCase):
    """Tests for the token refresh endpoint."""

    def setUp(self):
        """Creates an active user and sets the refresh token cookie for
        token refresh tests."""
        self.user = create_active_user()
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['refresh_token'] = str(refresh)

    def test_refresh_success(self):
        """Checks that a valid refresh cookie returns a new access token."""
        response = self.client.post('/api/token/refresh/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.cookies)

    def test_refresh_missing_cookie(self):
        """Checks that a missing refresh cookie returns 400."""
        self.client.cookies.clear()
        response = self.client.post('/api/token/refresh/')
        self.assertEqual(response.status_code, 400)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class PasswordResetViewTests(APITestCase):
    """Tests for the password reset request endpoint."""

    def setUp(self):
        """Creates an active user for password reset tests."""
        self.user = create_active_user(email='reset@example.com')

    def test_reset_existing_email(self):
        """Checks that a reset request for an existing email returns 200."""
        response = self.client.post(
            '/api/password_reset/', {'email': 'reset@example.com'}
        )
        self.assertEqual(response.status_code, 200)

    def test_reset_nonexistent_email(self):
        """Checks that a reset request for an unknown email still returns
        200 to avoid user enumeration."""
        response = self.client.post(
            '/api/password_reset/', {'email': 'nobody@example.com'}
        )
        self.assertEqual(response.status_code, 200)


class PasswordConfirmViewTests(APITestCase):
    """Tests for the password reset confirmation endpoint."""

    def setUp(self):
        """Creates an active user and generates a valid UID and token for
        password confirm tests."""
        self.user = create_active_user(email='confirm@example.com')
        self.uid, self.token = make_uid_token(self.user)

    def test_confirm_success(self):
        """Checks that a valid token and matching passwords reset the
        password successfully."""
        response = self.client.post(
            f'/api/password_confirm/{self.uid}/{self.token}/',
            {
                'new_password': 'NewPass1234!',
                'confirm_password': 'NewPass1234!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass1234!'))

    def test_confirm_password_mismatch(self):
        """Checks that mismatched passwords return 400."""
        response = self.client.post(
            f'/api/password_confirm/{self.uid}/{self.token}/',
            {
                'new_password': 'NewPass1234!',
                'confirm_password': 'Different!',
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_confirm_invalid_token(self):
        """Checks that an invalid token returns 400."""
        response = self.client.post(
            f'/api/password_confirm/{self.uid}/invalidtoken/',
            {
                'new_password': 'NewPass1234!',
                'confirm_password': 'NewPass1234!',
            },
        )
        self.assertEqual(response.status_code, 400)
