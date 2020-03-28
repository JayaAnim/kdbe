from . import gcloud
    

class App:

    def __init__(self):
        self.gcloud = gcloud.Gcloud()

    def deploy(self, *args, **kwargs):
        return self.gcloud.run("app", "deploy", *args, **kwargs)
