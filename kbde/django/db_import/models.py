from django.db import models
from kbde.django import models as kbde_models
from kbde.django.bg_process import models as kbde_bg_models

import tempfile, uuid, csv


def get_source_upload_to(obj, file_name):
    return f"import/source_file/{uuid.uuid4()}/{file_name}"


class ImportFile(kbde_bg_models.BgProcessModel):
    time_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    source = models.FileField(upload_to=get_source_upload_to)

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.local_source_path = None
        self.column_dict = None

    def bg_process(self):
        self.create_columns()
        self.create_rows()

    def create_columns(self):
        """
        Creates columns from the source file
        """
        local_source_path = self.get_local_source_path()

        with open(local_source_path) as local_source:
            reader = csv.DictReader(local_source)
            column_names = reader.fieldnames

        for column_name in column_names:
            column = ImportColumn.objects.get_or_create(
                name=column_name,
                import_file=self,
            )

    def create_rows(self):
        """
        Creates rows from the source file
        """
        local_source_path = self.get_local_source_path()

        with open(local_source_path) as local_source:
            reader = csv.DictReader(local_source)

            for row_dict in reader:
                row = ImportRow.create_from_dict(self, row_dict)

    def get_local_source_path(self):

        if self.local_source_path is None:

            # Need to download the source to a tempfile
            with tempfile.NamedTemporaryFile(delete=False) as local_source:
                local_source.write(self.source.read())

            self.local_source_path = local_source.name

        return self.local_source_path

    def get_column_dict(self):

        if not self.column_dict:
            columns = self.importcolumn_set.all()
            self.column_dict = {column.name: column for column in columns}

        return self.column_dict

class ImportColumn(models.Model):
    import_file = models.ForeignKey(ImportFile, on_delete=models.CASCADE)
    name = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)

    def __str__(self):
        return self.name


class ImportRow(models.Model):
    import_file = models.ForeignKey(ImportFile, on_delete=models.CASCADE)

    @classmethod
    def create_from_dict(cls, import_file, data):
        assert isinstance(data, dict)

        column_dict = import_file.get_column_dict()

        row = cls(import_file=import_file)
        row.save()

        value_list = []

        for key, value in data.items():
            column = column_dict.get(key)

            if column is None:
                continue

            value = ImportValue(
                column=column,
                row=row,
                value=value,
            )

            value_list.append(value)

        ImportValue.objects.bulk_create(value_list)

        return row


class ImportValue(models.Model):
    column = models.ForeignKey(ImportColumn, on_delete=models.CASCADE)
    row = models.ForeignKey(ImportRow, on_delete=models.CASCADE)
    value = models.TextField()

    def __str__(self):
        return f"{self.column}"
