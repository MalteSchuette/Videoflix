from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Validates and creates a new user with email and matching passwords."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """Checks that password and confirmed_password match."""
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return data

    def create(self, validated_data):
        """Removes the confirmation field and creates the user via the
        custom user manager."""
        validated_data.pop('confirmed_password')
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializes basic user information (id and email)."""

    class Meta:
        model = User
        fields = ['id', 'email']


class PasswordResetSerializer(serializers.Serializer):
    """Validates the email address for a password reset request."""

    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    """Validates that the new password and confirmation password match."""

    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        """Checks that new_password and confirm_password match."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return data
