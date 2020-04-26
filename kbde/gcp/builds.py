from . import gcloud
    

class Builds(gcloud.Gcloud):

    def submit(self, *args, **kwargs):
        return self.run_raw("builds", "submit", *args, **kwargs)
