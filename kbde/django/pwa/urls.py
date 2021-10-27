from . import views


app_name = "pwa"

urlpatterns = [
    views.Manifest.get_urls_path("pwa/manifest.json"),
    views.ServiceWorker.get_urls_path("pwa_service_worker.js"),
    views.Install.get_urls_path("pwa/install.js"),
]
