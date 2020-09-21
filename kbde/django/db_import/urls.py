from django.urls import path

from . import views


app_name = "kbde_django_db_import"

urlpatterns = [
    path("file/", views.ImportFileList.as_view(), name="file_list"),
    path("file/create", views.ImportFileCreate.as_view(), name="file_create"),
    path("file/<int:related_pk>/row/", views.ImportRowList.as_view(), name="row_list"),
    path("mapping/", views.ImportMappingList.as_view(), name="mapping_list"),
    path("mapping/<str:model_name>/create", views.ImportMappingCreate.as_view(), name="mapping_create"),
    path("mapping/type/select", views.ImportMappingTypeSelect.as_view(), name="mapping_type_select"),
    path("mapping/<int:related_pk>/mapping_column/", views.ImportMappingColumnList.as_view(), name="mapping_column_list"),
    path("mapping/<int:related_pk>/mapping_column/create", views.ImportMappingColumnCreate.as_view(), name="mapping_column_create"),
    path("mapping/<int:related_pk>/mapping_row/", views.ImportMappingRowList.as_view(), name="mapping_row_list"),
    path("mapping/<int:pk>/complete", views.ImportMappingComplete.as_view(), name="mapping_complete"),
    path("", views.ImportList.as_view(), name="list"),
    path("create", views.ImportCreate.as_view(), name="create"),
]
