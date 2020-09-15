from kbde import kbde_cli, api_client

import os


class Base(kbde_cli.Command):
    
    api_client_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api_client = self.get_api_client()

    def handle(self, **options):
        try:
            return self.handle_client(**options)
        except api_client.Client.ApiClientException as e:
            self.stdout.write(str(e))

    def handle_client(self, **options):
        raise NotImplementedError(f"{self.__class__.__name__} must implement .handle_client()")
        
    def get_api_client(self):
        api_token = os.getenv("KBDE_DO_API_TOKEN")
        api_client_class = self.get_api_client_class()

        return api_client_class(api_token=api_token)

    def get_api_client_class(self):
        return self.api_client_class


class GetCommand(Base):
    """
    A command which runs an API get
    """
    
    def handle_client(self, **options):
        return self.api_client.get(**options)
