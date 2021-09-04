from .views import token


app_name = "token_auth"

urlpatterns = [
    token.AuthTokenCreate.get_urls_path("token/create"),
]
