from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """JWT authentication that reads the token from an HttpOnly cookie
    instead of the Authorization header."""

    def authenticate(self, request):
        """Reads the access token from the request cookie instead of
        the Authorization header."""
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None
        validated_token = self.get_validated_token(access_token)
        return self.get_user(validated_token), validated_token
