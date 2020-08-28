from django import views
from kbde.django import mixins as kbde_mixins

from . import models


class ImportFileCreate(views.generic.CreateView):
    template_name = "kbde_django_db_import/import_file/create.html"
    model = models.ImportFile


class ImportFileList(views.generic.ListView):
    template_name = "kbde_django_db_import/import_file/list.html"
    model = models.ImportFile


class ImportRowList(kbde_mixins.RelatedObject, views.generic.ListView):
    template_name = "kbde_django_db_import/import_row/list.html"
    model = models.ImportRow
    import_file_orm_path = "import_file"
    import_file_model = models.ImportFile


class ImportMappingCreate(views.generic.CreateView):
    template_name = "kbde_django_db_import/import_mapping/create.html"
    model = models.ImportMapping


class ImportMappingList(views.generic.ListView):
    template_name = "kbde_django_db_import/import_mapping/list.html"
    model = models.ImportMapping


class ImportMappingRowList(kbde_mixins.RelatedObject, views.generic.ListView):
    template_name = "kbde_django_db_import/import_mapping_row/list.html"
    model = models.ImportMappingRow
    import_mapping_orm_path = "import_mapping"
    import_mapping_model = models.ImportMapping


class ImportCreate(views.generic.CreateView):
    template_name = "kbde_django_db_import/import/create.html"
    model = models.Import


class ImportList(views.generic.ListView):
    template_name = "kbde_django_db_import/import/list.html"
    model = models.Import
