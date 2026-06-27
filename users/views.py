from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Registration successful.",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "role": user.role,
                }
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "message": "Login successful.",
                "access": serializer.validated_data['access'],
                "refresh": serializer.validated_data['refresh'],
            },
            status=status.HTTP_200_OK
        )


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Logout successful."},
            status=status.HTTP_205_RESET_CONTENT
        )