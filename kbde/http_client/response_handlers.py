

class ResponseHandler:
    content_types = []

    def get_content_types(self):
        assert self.content_types, (
            f"{self.__class__} must define .content_types"
        )

        return self.content_types.copy()

    def handle(self, response):
        raise NotImplementedError


class TextResponseHandler(ResponseHandler):
    content_types = [
        "text/html",
    ]

    def handle(self, response):
        return response.text


class JsonResponseHandler(ResponseHandler):
    content_types = [
        "application/json",
    ]
    
    def handle(self, response):
        return response.json()
