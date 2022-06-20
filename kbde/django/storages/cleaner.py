from django.apps import apps
from django.db.models import Q
from django.core.files import storage


class Cleaner:
    
    def __init__(self, stdout=None):
        self.stdout = stdout
        self.model_storage_field_map = self.get_model_storage_field_map()

    def get_model_storage_field_map(self):
        model_storage_field_map = {}

        for app_name, model_map in apps.all_models.items():

            for model_name, model in model_map.items():
                model_fields = model._meta.get_fields()

                for field in model_fields:

                    if hasattr(field, "storage"):
                        storage_field_names = (
                            model_storage_field_map.get(model, [])
                        )
                        storage_field_names.append(field.name)
                        model_storage_field_map[model] = storage_field_names

        return model_storage_field_map
    
    def clean(self, dry_run=True):

        for path in self.get_storage_paths():
            path_in_database = self.check_path_in_database(path)

            if not dry_run and not path_in_database:
                self.delete_object(path)

            if dry_run and self.stdout is not None:
                if path_in_database:
                    self.stdout.write(f"found: {path}")
                else:
                    self.stdout.write(f"delete: {path}")

    def check_path_in_database(self, path):
        """
        Check all models and all fields that are present in
        self.model_storage_field_map. If the path is found,
        return True. Otherwise return False.
        """
        for model, field_names in self.model_storage_field_map.items():
            query = None

            for field_name in field_names:
                field_query = Q(**{field_name: path})

                if query is None:
                    query = field_query
                else:
                    query = query | field_query

            if model.objects.filter(query).exists():
                return True

        return False

    def get_storage_objects(self):
        raise NotImplementedError(
            f"{self.__class__} must implement .get_storage_objects()"
        )

    def delete_storage_object(self, path):
        raise NotImplementedError(
            f"{self.__class__} must implement .delete_storage_object()"
        )


class S3Cleaner(Cleaner):
    
    def get_storage_paths(self):
        return storage.default_storage.get_all_keys("")

    def delete_object(self, path):
        storage.default_storage.delete(path)
