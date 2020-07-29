from . import gcloud

import sys
    

class App(gcloud.Gcloud):

    def deploy(self, *args, **kwargs):
        return self.run("app", "deploy", *args, **kwargs)

    def list_versions(self, *args, **kwargs):
        try:
            return self.run("app", "versions", "list", *args, **kwargs)
        except self.GcloudException as e:
            if e.error_has_terms("service", "not found"):
                raise self.ServiceNotFound
            raise

    def delete_version(self, service, version_id, **kwargs):
        return self.run("app", "versions", "delete", version_id, service=service, quiet="", **kwargs)

    class AppException(Exception):
        pass

    class ServiceNotFound(AppException):
        pass
