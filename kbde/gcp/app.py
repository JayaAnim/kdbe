from . import gcloud
    

class App:

    def __init__(self):
        self.gcloud = gcloud.Gcloud()

    def deploy(self, *args, **kwargs):
        return self.gcloud.run("app", "deploy", *args, **kwargs)

    def list_versions(self, *args, **kwargs):
        return self.gcloud.run("app", "versions", "list", *args, **kwargs)

    def delete_version(self, service, version_id):
        return self.gcloud.run("app", "versions", "delete", version_id, service=service, quiet="")
