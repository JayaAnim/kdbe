from . import gcloud
    

class Builds:

    def __init__(self):
        self.gcloud = gcloud.Gcloud()

    def submit(self, *args, **kwargs):
        return self.gcloud.run_raw("builds", "submit", *args, **kwargs)
