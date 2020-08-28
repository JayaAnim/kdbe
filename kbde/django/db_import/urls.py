from django.urls import path

from . import views


app_name = "kbde_django_db_import"

urlpatterns = [
    path("file/", views.ImportFileList.as_view(), name="file_list"),
    path("file/create", views.ImportFileCreate.as_view(), name="file_create"),
    path("file/<int:pk>/row/", views.ImportRowList.as_view(), name="row_list"),
    path("mapping/", views.ImportMappingList.as_view(), name="mapping_list"),
    path("mapping/create", views.ImportMappingCreate.as_view(), name="mapping_create"),
]
