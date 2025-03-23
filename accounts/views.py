from django.contrib.auth import get_user_model, login, authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, PasswordChangeSerializer
from rest_framework.views import APIView

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    # @swagger_auto_schema(
    #     operation_description="Login user and get JWT tokens",
    #     responses={
    #         200: openapi.Response(
    #             description="Login successful",
    #             schema=openapi.Schema(
    #                 type=openapi.TYPE_OBJECT,
    #                 properties={
    #                     'user': UserSerializer,
    #                     'access_token': openapi.Schema(type=openapi.TYPE_STRING),
    #                     'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
    #                 }
    #             )
    #         ),
    #         400: "Bad Request"
    #     }
    # )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

class PasswordChangeView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"error": "Invalid old password"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"message": "Password changed successfully"})

class GoogleAuthView(APIView):
    def post(self, request, *args, **kwargs):
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

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer 
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all users",
        responses={
            200: openapi.Response(
                description="List of users",
                schema=UserSerializer(many=True)
            ),
            401: "Unauthorized"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating the authenticated user's profile"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get authenticated user's profile",
        responses={
            200: openapi.Response(
                description="User profile details",
                schema=UserSerializer
            ),
            401: "Unauthorized"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update authenticated user's profile",
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=UserSerializer
            ),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        # Add any additional logic before saving
        serializer.save()


class LogoutView(generics.GenericAPIView):
    """View for user logout"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout user and invalidate token",
        responses={
            200: openapi.Response(
                description="Successfully logged out",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Unauthorized"
        }
    )
    def post(self, request):
        try:
            # Get the token from the request
            auth_header = request.headers.get('Authorization')
            if auth_header and ' ' in auth_header:
                token = auth_header.split(' ')[1]
                # Add token to blacklist
                RefreshToken(token).blacklist()
            
            return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Error during logout'}, status=status.HTTP_400_BAD_REQUEST)
