from django.urls import path

from . import views

app_name = "orgs"

urlpatterns = [
    path("groups/", views.group_search, name="group_search"),
    path("groups/create/", views.group_create, name="group_create"),
    path("groups/<int:pk>/edit/", views.group_edit, name="group_edit"),
    path("groups/<int:pk>/delete/", views.group_delete, name="group_delete"),
]
