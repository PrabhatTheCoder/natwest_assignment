from django.shortcuts import render

# Create your views here.

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import CustomUserSerializer



class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register a new user and return a JWT token.
        """
        serializer = CustomUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "user": serializer.data,
                "access": access_token,
                "refresh": str(refresh)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Log in the user, and return JWT tokens.
        """
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "user": {"email": user.email, "name": user.name},
                "access": access_token,
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)


class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Log out the user by blacklisting the refresh token.
        """
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({"message": "Successfully logged out."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
