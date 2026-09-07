from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("confirm/", views.confirm, name="confirm"),
    path("login/", views.StubLoginView.as_view(), name="login"),
    path("logout/", views.StubLogoutView.as_view(), name="logout"),
    path("network-mode/", views.network_mode, name="network_mode"),
    path("users/", views.user_search, name="user_search"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
]
