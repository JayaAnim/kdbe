import tempfile, os, csv


class Loader:
    chunk_size = 100000

    def load(self, object_list):
        load_object_list = []
        
        for obj in object_list:
            load_object_list.append(obj)

            if len(load_object_list) >= self.chunk_size:
                # Flush the object list into the destination
                self.load_into_destination(load_object_list)
                load_object_list = []

        if load_object_list:
            self.load_into_destination(load_object_list)

    def load_into_destination(self, object_list):
        raise NotImplementedError(
            f"{self.__class__} must implement .load_into_destination()"
        )


class FileLoader(Loader):
    file_path = None
    
    def load_into_destination(self, object_list):
        with open(self.get_file_path(), "a") as open_file:
            self.load_file(open_file, object_list)

    def get_file_path(self):
        assert self.file_path, (
            f"{self.__class__} must define .file_path or override "
            f".get_file_path()"
        )
        return self.file_path

    def load_file(self, open_file, object_list):
        raise NotImplementedError(
            f"{self.__class__} must implement .load_file()",
        )


class CsvLoader(FileLoader):
    field_names = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_written = False

    def load_file(self, open_file, object_list):
        field_names = self.get_field_names()
        csv_writer = csv.DictWriter(open_file, fieldnames=field_names)
        for obj in object_list:
            if not self.header_written:
                csv_writer.writeheader()
                self.header_written = True

            obj = {field_name: obj[field_name] for field_name in field_names}
            csv_writer.writerow(obj)

    def get_field_names(self):
        assert self.field_names, (
            f"{self.__class__} must define .field_names"
        )
        return self.field_names


class SnowflakeLoader(Loader):
    database_name = None
    schema_name = None
    warehouse_name = None
    table_name = None
    field_names = []
    snowflake_username = None
    snowflake_password = None
    snowflake_account = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection = self.get_snowflake_connection()

    def load_into_destination(self, object_list):
        field_names = self.get_field_names()

        with tempfile.NamedTemporaryFile("w", delete=False) as temp:
            writer = csv.DictWriter(temp, fieldnames=field_names)

            for obj in object_list:
                writer.writerow(
                    {field_name: obj[field_name] for field_name in field_names}
                )

        # Send the written tempfile to snowflake
        self.connection.cursor().execute(f"PUT file://{temp.name}* @%{self.table_name}")
        self.connection.cursor().execute(f"copy into {self.table_name} file_format = (type = csv field_optionally_enclosed_by='\"')")

        # Remove the tempfile
        os.remove(temp.name)

    def get_insert_field_names(self):
        return ", ".join(self.get_field_names())

    def get_values_placeholder(self): 
        return ", ".join(["%s"]* len(self.get_field_names()))

    def get_field_names(self):
        assert self.field_names, (
            f"{self.__class__} must define .field_names"
        )
        return self.field_names

    def get_snowflake_connection(self):
        from snowflake import connector

        return connector.connect(
			user=self.snowflake_username,
            password=self.snowflake_password,
            account=self.snowflake_account,
            warehouse=self.warehouse_name,
            database=self.database_name,
            schema=self.schema_name,
        )
