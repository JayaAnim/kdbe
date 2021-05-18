from . import views

app_name = "login_link"

urlpatterns = [
    views.LoginLinkCreate.get_urls_path("login_link/create"),
    views.LoginLinkAuthenticate.get_urls_path("login_link/<uuid:slug>/authenticate"),
    views.LoginLinkConfirm.get_urls_path("login_link/<uuid:secret>/confirm"),
    views.LoginLinkConfirmResult.get_urls_path("login_link/<uuid:slug>/result"),
]
