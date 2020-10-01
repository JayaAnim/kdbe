from kbde.django.bg_process import models as kbde_bg_models


class Scrape(kbde_bg_models.BgProcessModel):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True)

    def bg_process(self):
        scraper
        


class Page(kbde_bg_models.BgProcessModel):
    scrape = models.ForeignKey(Scrape, on_delete=models.CASCADE)
    url = models.URLField()
    
    def bg_process(self):
        
