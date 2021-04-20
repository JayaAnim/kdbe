import tempfile, csv, os, json


class Extractor:

    def extract(self, page_number=None):

        if page_number is not None:
            # Get a single page
            object_list = self.get_page(page_number)

            # Return results
            for obj in object_list:
                yield obj
        
        else:
            page_number = 1

            while True:
                object_list = self.get_page(page_number)

                if object_list is None:
                    break

                for obj in object_list:
                    yield obj

                page_number += 1

    def get_page(self, page_number):
        raise NotImplementedError(
            f"{self.__class__} must implement .get_page()"
        )


class FileExtractor(Extractor):
    file_path = None
    
    def get_page(self, page_number):
        if page_number > 1:
            return None

        with open(self.get_file_path()) as open_file:
            return self.process_file(open_file)

    def get_file_path(self):
        assert self.file_path, (
            f"{self.__class__} must define .file_path or override "
            f".get_file_path()"
        )
        return self.file_path

    def process_file(self, open_file):
        raise NotImplementedError(
            f"{self.__class__} must implement .process_file()",
        )


class JsonFileExtractor(FileExtractor):
    
    def process_file(self, open_file):
        json_string = open_file.read()
        data = json.loads(json_string)
        return self.get_data_list(data)

    def get_data_list(self, data):
        assert isinstance(data, list), (
            f"{self.__class__} .get_data_list() must return a list. Override "
            f"this function to return a list of data."
        )
        return data


class HttpExtractor(Extractor):
    
    def get_page(self, page_number):
        import requests

        url = self.get_url(page_number)
        response = requests.get(url)

        return self.get_object_list_from_response(response, url, page_number)

    def get_url(self, page_number):
        raise NotImplementedError(
            f"{self.__class__} must implement .get_url()"
        )

    def get_object_list_from_response(self, response, url, page_number):
        return NotImplementedError(
            f"{self.__class__} must implement .get_object_list_from_response()"
        )


class S3Extractor(Extractor):
    bucket_name = None
    bucket_path = None
    bucket_path_complete = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = self.get_s3_client()
        self.page_path_list = self.get_page_path_list()

    def get_s3_client(self):
        import boto3
        return boto3.client("s3")

    def get_page_path_list(self):
        """
        Returns a mapping of all of the files which need to be processed by this extractor
        """
        response = self.client.list_objects(Bucket=self.bucket_name, Prefix=self.get_bucket_path())
        return [obj["Key"] for obj in response["Contents"]]

    def get_bucket_path(self):
        return self.bucket_path
    
    def get_page(self, page_number):
        """
        Downloads a file from s3
        returns the content as a list of objects
        """
        file_path = self.download_to_tempfile(page_number)

        if file_path is None:
            return None

        return self.get_object_list_from_file(file_path)

    def download_to_tempfile(self, page_number):
        """
        Gets the s3 object key
        Downloads the file to the local environment
        Returns the file path
        """
        key = self.get_path_from_page_number(page_number)

        if key is None:
            return None

        with tempfile.NamedTemporaryFile(delete=False) as temp:
            self.client.download_fileobj(self.bucket_name, key, temp)

        return temp.name

    def get_path_from_page_number(self, page_number):
        try:
            return self.page_path_list[page_number-1]
        except IndexError:
            # There was no file at this page number
            # No more files to process
            return None

    def get_object_list_from_file(self, file_path):
        with open(file_path) as open_file:
            reader = csv.DictReader(open_file)

            for obj in reader:
                yield obj
                
        # Finished reading from the file, and it's closed
        # Remove it from the system
        os.remove(file_path)
