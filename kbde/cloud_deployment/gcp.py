from kbde import api_client

from . import leader


class MetadataBase(api_client.Client):
    host = "http://metadata.google.internal"
    headers = {
        "Metadata-Flavor": "Google",
    }


class AppEngineBase(api_client.Client):
    host = "https://appengine.googleapis.com"
    headers = {
        "Authorization": "Bearer {auth_token}",
    }


class InstanceId(MetadataBase):
    path = "/computeMetadata/v1/instance/name"


class ProjectId(MetadataBase):
    path = "/computeMetadata/v1/instance/attributes/gae_project"


class Service(MetadataBase):
    path = "/computeMetadata/v1/instance/attributes/gae_backend_name"


class Version(MetadataBase):
    path = "/computeMetadata/v1/instance/attributes/gae_backend_version"


class AuthToken(MetadataBase):
    path = "/computeMetadata/v1/instance/service-accounts/default/token"


class InstanceList(AppEngineBase):
    path = "/v1/apps/{project_id}/services/{service}/version/{version}/instances/"


class GcpLeader(leader.Leader):
    """
    Requires that the project's App Engine Admin API is enabled
    """
    METADATA_CLIENTS = {
        "instance_id_client": InstanceId,
        "project_id_client": ProjectId,
        "service_client": Service,
        "version_client": Version,
        "auth_token_client": AuthToken,
        "instance_list_client": InstanceList,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_clients()

    def create_clients(self):
        # Create metadata clients
        for class_name, client_class in self.METADATA_CLIENTS.items():
            setattr(self, class_name, client_class())

    def get_all_instance_ids(self):
        """
        Get all instance ids for this same zone and project
        """
        project_id = self.get_project_id()
        service = self.get_service()
        version = self.get_version()
        auth_token = self.get_auth_token()

        result = self.instance_list_client.get(
            project_id=project_id,
            service=service,
            version=version,
            auth_token=auth_token,
        )

        print(result)

    def get_project_id(self):
        """
        Get the project ID for this instance
        """
        return self.project_id_client.get()

    def get_service(self):
        """
        Get the ID of the service for this instance
        """
        return self.service_client.get()

    def get_version(self):
        """
        Return the version for this instance
        """
        return self.version_client.get()
    
    def get_instance_id(self):
        """
        Get the id for this instance
        """
        return self.instance_id_client.get()

    def get_auth_token(self):
        """
        Get an auth token from the metatdata server
        """
        result = self.auth_token_client.get()
        return result.get("access_token")
