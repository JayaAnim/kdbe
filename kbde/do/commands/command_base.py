from kbde.kbde_cli import command

import os, io, json


class Base(command.Command):
    
    api_client_class = None
    list_arguments = []

    def handle(self, **options):
        from kbde.api_client import client
        import yaml

        self.api_client = self.get_api_client_class()()

        for key, value in options.items():
            if value and key in self.list_arguments:
                options[key] = value.split(",")

        try:
            result = self.handle_client(**options)

        except client.Client.ApiClientException as e:
            try:
                result = json.loads(str(e))
            except ValueError:
                result = ""

        if not result:
            return ""

        str_result = io.StringIO()
        yaml.dump(result, str_result)

        return str_result.getvalue()

    def handle_client(self, **options):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement .handle_client()"
        )

    def get_api_client_class(self):
        return self.api_client_class


class GetCommand(Base):
    """
    A command which runs an API GET operation
    """
    
    def handle_client(self, **options):
        return self.api_client.get(**options)


class PostCommand(Base):
    """
    A command which runs and API POST operation
    """

    def handle_client(self, **options):
        return self.api_client.post(**options)


class DeleteCommand(Base):
    """
    A command which runs and API POST operation
    """

    def handle_client(self, **options):
        return self.api_client.delete(**options)
