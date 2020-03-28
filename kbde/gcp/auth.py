from . import gcloud


class Auth:
    
    def __init__(self):
        self.gcloud = gcloud.Gcloud()

    def activate_service_account(self, email, key_file):
        kwargs = {
            "key-file": key_file,
        }
        return self.gcloud.run("auth", "activate-service-account", email, **kwargs)
