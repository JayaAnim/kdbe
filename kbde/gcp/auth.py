from . import gcloud


class Auth(gcloud.Gcloud):

    def activate_service_account(self, email, key_file):
        kwargs = {
            "key-file": key_file,
        }
        return self.run("auth", "activate-service-account", email, **kwargs)
