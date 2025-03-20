from django.urls import path
from .views import (
    UserListView, GoogleAuthView, RegisterView,
    LoginView, PasswordChangeView
)

urlpatterns = [
    path("auth/google/", GoogleAuthView.as_view(), name="google-auth"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"), 
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
]