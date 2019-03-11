from kbde.api_client import client


class Rep(client.Client):
    host = "https://govbuddy.com"
    path = "/api/v1/legislators"
    headers = {
        "Authorization": "Token {auth_token}"
        }

r = Rep(auth_token="9959fa508e08cf7540278759ef9378a22644912c")
