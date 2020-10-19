from django.db import models
from django.core import exceptions
from polymorphic import models as poly_models
from kbde.django import models as kbde_models
from kbde.django.bg_process import models as kbde_bg_models

import tempfile, uuid, csv


def get_source_upload_to(obj, file_name):
    return f"import/source_file/{uuid.uuid4()}/{file_name}"


# Input data


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

        with open(local_source_path, encoding="latin1") as local_source:
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

        with open(local_source_path, encoding="latin1") as local_source:
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
            columns = self.get_import_columns()
            self.column_dict = {column.name: column for column in columns}

        return self.column_dict

    def get_import_rows(self):
        start_index = 0

        while True:
            import_rows = self.get_import_row_page(start_index)

            if not import_rows:
                break

            for import_row in import_rows:
                yield import_row

            start_index += 1000
        
    def get_import_row_page(self, start_index):
        return self.importrow_set.order_by("id")[start_index:start_index+1000]

    def get_import_row_count(self):
        return self.importrow_set.count()

    def get_import_columns(self):
        return self.importcolumn_set.order_by("id")


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

    def get_import_column_values(self):
        columns = self.import_file.get_import_columns()
        data = self.get_data()
        
        for column in columns:
            column.value = data[column.name]

        return columns

    def get_data(self):
        values = self.importvalue_set.select_related("column")
        return {value.column.name: value.value for value in values}


class ImportValue(models.Model):
    column = models.ForeignKey(ImportColumn, on_delete=models.CASCADE)
    row = models.ForeignKey(ImportRow, on_delete=models.CASCADE)
    value = models.TextField()

    def __str__(self):
        return f"{self.column}"


# Mappings


class ImportMapping(poly_models.PolymorphicModel, kbde_bg_models.BgProcessModel):
    model = None
    import_fields = []
    form_field_names = [
        "import_file",
    ]

    import_file = models.ForeignKey(ImportFile, on_delete=models.CASCADE)

    @classmethod
    def get_model_name(cls):
        return cls.__name__

    def __str__(self):
        return self.import_file.name

    def queue_bg_process(self):
        if self.importmappingcolumn_set.exists():
            return super().queue_bg_process()

    def bg_process(self):
        self.create_rows()

    def create_rows(self):
        for row in self.import_file.get_import_rows():
            mapping_row = ImportMappingRow(
                mapping=self,
                row=row,
            )
            mapping_row.clean()
            mapping_row.save()

    def get_instance_lookup_data(self):
        """
        Override this to add constants to the import
        """
        return {}

    def update_mapping_row_data(self, data):
        return data

    def get_import_mapping_rows(self):
        start_index = 0

        while True:
            import_mapping_rows = self.get_import_mapping_row_page(start_index)

            if not import_mapping_rows:
                break

            for import_mapping_row in import_mapping_rows:
                yield import_mapping_row

            start_index += 1000
        
    def get_import_mapping_row_page(self, start_index):
        return self.importmappingrow_set.order_by("id")[start_index:start_index+1000]

    def save_instance(self, instance):
        instance.save()

        return instance

    def get_columns_display(self):
        mapping_columns = self.get_import_mapping_columns()
        return ", ".join(mc.column.name for mc in mapping_columns)

    def get_import_fields_display(self):
        mapping_columns = self.get_import_mapping_columns()
        return ", ".join(mc.import_field for mc in mapping_columns)
        
    def get_import_mapping_columns(self):
        return self.importmappingcolumn_set.order_by("id")

    def modify_form(self, form):
        return form


class ImportMappingColumn(models.Model):
    mapping = models.ForeignKey(ImportMapping, on_delete=models.CASCADE)
    import_field = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    column = models.ForeignKey(ImportColumn, on_delete=models.CASCADE)
    is_identifier = models.BooleanField(default=False, help_text="Should this column be used to look up an existing model?")

    class Meta:
        unique_together = ("mapping", "import_field", "column")

    def clean(self):
        if self.import_field not in self.mapping.import_fields:
            import_fields = ", ".join(self.mapping.import_fields)
            raise exceptions.ValidationError(f'import_field, "{self.import_field}", is not valid. Choices are: {import_fields}')


class ImportMappingRow(models.Model):
    STATUS_GOOD = "good"
    STATUS_BAD = "bad"
    STATUS_CHOICES = (
        (STATUS_GOOD, "Good"),
        (STATUS_BAD, "Bad"),
    )

    mapping = models.ForeignKey(ImportMapping, on_delete=models.CASCADE)
    row = models.ForeignKey(ImportRow, on_delete=models.CASCADE)
    status = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, choices=STATUS_CHOICES)
    new_instance = models.BooleanField(default=True)
    status_message = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD, blank=True)

    def clean(self):
        if not self.status:
            self.set_instance_status()

    def save_instance(self):
        instance = self.set_instance_status()
        
        if self.status == self.STATUS_GOOD:
            self.mapping.save_instance(instance)

    def set_instance_status(self):
        try:
            instance = self.get_instance()
        except self.mapping.model.MultipleObjectsReturned:
            self.status = self.STATUS_BAD
            self.status_message = "Multiple objects found when looking up existing models"

        if instance is None:
            instance = self.mapping.model()
            self.new_instance = True
        else:
            self.new_instance = False

        try:
            instance = self.update_instance(instance)
            self.status = self.STATUS_GOOD

        except exceptions.ValidationError as e:
            self.status_message = str(e)
            self.status = self.STATUS_BAD
        except self.RelatedLookupValue as e:
            self.status = self.STATUS_BAD
            self.status_message = str(e)

        self.save()

        return instance

    def update_instance(self, instance):
        # Get new data to update
        data = self.get_data()

        for key, value in data.items():
            setattr(instance, key, value)

        instance.clean()

        return instance
    
    def get_instance(self):
        lookup_data = self.get_instance_lookup_data()

        if not lookup_data:
            return None

        try:
            return self.mapping.model.objects.get(**lookup_data)
        except self.mapping.model.DoesNotExist:
            return None
        
    def get_instance_lookup_data(self):
        row_data = self.row.get_data()

        identifier_mapping_columns = self.mapping.importmappingcolumn_set.filter(
            is_identifier=True
        ).select_related("column")

        lookup_data = {
            mapping_column.import_field: row_data[mapping_column.column.name]
            for mapping_column in identifier_mapping_columns
        }

        lookup_data.update(self.mapping.get_instance_lookup_data())

        return lookup_data

    def get_data(self):
        row_data = self.row.get_data()

        identifier_mapping_columns = self.mapping.importmappingcolumn_set.select_related("column")

        data = {
            mapping_column.import_field: row_data[mapping_column.column.name]
            for mapping_column in identifier_mapping_columns
        }

        data = self.mapping.update_mapping_row_data(data)

        new_data = {}

        for key, value in data.items():

            if "__" in key:
                # This is a model relationship
                key_parts = key.split("__")

                related_model_name = key_parts[0]

                foreign_key_field = getattr(
                    self.mapping.model,
                    related_model_name,
                    None,
                )

                assert foreign_key_field is not None, (
                    f"related_model_name `{related_model_name}` nor found"
                )

                model = foreign_key_field.field.related_model

                lookup = new_data.get(related_model_name, {
                    "model": model,
                    "query": {},
                })
                
                query_key = "__".join(key_parts[1:])
                lookup["query"][query_key] = value

                new_data[related_model_name] = lookup

            else:
                new_data[key] = value

        for key, value in new_data.items():
            if (
                isinstance(value, dict)
                and "model" in value
                and "query" in value
            ):
                model = value["model"]
                query = value["query"]

                try:
                    obj = model.objects.get(**query)
                except model.DoesNotExist:
                    raise self.RelatedLookupValue(
                        f"Related {model.__name__} not found"
                    )
                except model.MultipleObjectsReturned:
                    raise self.RelatedLookupValue(
                        f"Multiple {model.__name__} found"
                    )

                new_data[key] = obj

        return new_data

    def get_import_mapping_column_values(self):
        columns = self.mapping.get_import_mapping_columns()
        data = self.get_data()
        
        for column in columns:
            column.value = data[column.column.name]

        return columns

    class RelatedLookupValue(Exception):
        """
        Exception for when a related model cannot be found
        """


class Import(kbde_bg_models.BgProcessModel):
    """
    The actual import of an ImportMapping
    """
    import_mapping = models.ForeignKey(ImportMapping, on_delete=models.CASCADE)

    def bg_process(self):
        
        for import_mapping_row in self.import_mapping.get_import_mapping_rows():
            import_mapping_row.save_instance()
