from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
# Create your views here.

class AuthAPI(ViewSet):
    permission_classes = [AllowAny]

    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
            "expiresIn": 1800,
            "role": user.role
        })


    def refresh(self, request):
        refresh_token = request.data.get("refreshToken")
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                "accessToken": str(refresh.access_token),
                "expiresIn": 1800
            })
        except Exception:
            return Response(
                {"message": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

    def logout(self, request):
        refresh_token = request.data.get("refreshToken")
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out"})
        except Exception:
            return Response(
                {"message": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )