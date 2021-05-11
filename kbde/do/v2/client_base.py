from kbde.api_client import client


class Base(client.Client):
    host = "https://api.digitalocean.com/v2"

    headers = {
        "Authorization": "Bearer {api_token}",
    }
