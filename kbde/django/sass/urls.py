from . import views


app_name = "sass"

urlpatterns = [
    views.Page.get_urls_path("sass/page.css"),
]
