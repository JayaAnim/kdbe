from kbde.api_client import client

import os


class Base(client.Client):
    host = "https://api.digitalocean.com/v2"

    headers = {
        "Authorization": "Bearer {api_token}",
    }

    def __init__(self, **params):
        params["api_token"] = params.get("api_token", os.getenv("KBDE_DO_API_TOKEN"))
        return super().__init__(**params)
