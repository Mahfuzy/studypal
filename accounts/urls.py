from django.urls import path
from .views import (
    UserListView, GoogleAuthView, RegisterView,
    LoginView, PasswordChangeView, UserProfileView, LogoutView
)

urlpatterns = [
    path("auth/google/", GoogleAuthView.as_view(), name="google-auth"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"), 
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
]