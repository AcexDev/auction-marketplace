from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'confirm_password']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")

        refresh = RefreshToken.for_user(user)

        return {
            'user': user,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs.get('refresh')
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception:
            raise serializers.ValidationError("Token is invalid or already blacklisted.")