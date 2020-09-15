from kbde import api_client


class Base(api_client.Client):
    host = "https://api.digitalocean.com/v2"

    headers = {
        "Authorization": "Bearer {api_token}",
    }
