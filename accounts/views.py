from django.contrib.auth import get_user_model, login, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, PasswordChangeSerializer

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response({"error": "Invalid old password"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"message": "Password changed successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleAuthView(APIView):
    def post(self, request):
        id_token = request.data.get("id_token")
        if not id_token:
            return Response({"error": "ID token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify token with Google
        google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        response = requests.get(google_url)
        if response.status_code != 200:
            return Response({"error": "Invalid ID token"}, status=status.HTTP_400_BAD_REQUEST)

        user_data = response.json()
        email = user_data.get("email")
        first_name = user_data.get("given_name", "")  
        last_name = user_data.get("family_name", "")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create user
        user, created = User.objects.get_or_create(email=email, defaults={"first_name": first_name, "last_name": last_name})

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Log in user for session authentication
        login(request, user)

        return Response({
            "message": "Authenticated",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "access_token": access_token,
            "refresh_token": str(refresh),
        }, status=status.HTTP_200_OK)
        


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Requires authentication to view users
