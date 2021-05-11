from django.urls import path
from django.contrib.auth import views as auth_views
from kbde.django import views


urlpatterns = [
    views.LoginView.get_urls_path("login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
]
