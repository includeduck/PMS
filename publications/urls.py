from django.urls import path

from . import views

app_name = "publications"

urlpatterns = [
    path("search/", views.search, name="search"),
    path("search/download-all/", views.download_all, name="download_all"),
    path("publications/upload/", views.upload, name="upload"),
    path("publications/mine/", views.mine, name="mine"),
    path("publications/<int:pk>/download/", views.download, name="download"),
    path("publications/<int:pk>/edit/", views.edit, name="edit"),
]
