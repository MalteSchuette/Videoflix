from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, UserSerializer, PasswordResetSerializer, PasswordConfirmSerializer
from ..utils import send_activation_email, send_password_reset_email

User = get_user_model()


def set_auth_cookies(response, access_token, refresh_token):
    """Sets access_token and refresh_token as HttpOnly cookies on the response."""
    response.set_cookie('access_token', str(access_token), httponly=True, samesite='Lax')
    response.set_cookie('refresh_token', str(refresh_token), httponly=True, samesite='Lax')


def delete_auth_cookies(response):
    """Deletes the JWT auth cookies from the response."""
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Registers a new user and sends an activation email."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_activation_email(user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class ActivateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Activates a user account using the uidb64 and token from the activation email."""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError):
            return Response({'error': 'Activation failed.'}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Activation failed.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        return Response({'message': 'Account successfully activated.'})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticates the user and sets JWT cookies on success."""
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password) or not user.is_active:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        response = Response({
            'detail': 'Login successful',
            'user': {'id': user.id, 'username': user.email},
        })
        set_auth_cookies(response, refresh.access_token, refresh)
        return response


class LogoutView(APIView):

    def post(self, request):
        """Logs out the user by blacklisting the refresh token and deleting auth cookies."""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token missing.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass
        response = Response(
            {'detail': 'Logout successful! All tokens will be deleted. Refresh token is now invalid.'}
        )
        delete_auth_cookies(response)
        return response


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Issues a new access token if the refresh token cookie is valid."""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token missing.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            access_token = token.access_token
        except TokenError:
            return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)
        response = Response({'detail': 'Token refreshed', 'access': str(access_token)})
        response.set_cookie('access_token', str(access_token), httponly=True, samesite='Lax')
        return response


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Sends a password reset email if a user with the given email exists."""
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            send_password_reset_email(user)
        return Response({'detail': 'An email has been sent to reset your password.'})


class PasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Resets the user's password after validating the uidb64 and token."""
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError):
            return Response({'error': 'Invalid link.'}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Your Password has been successfully reset.'})
