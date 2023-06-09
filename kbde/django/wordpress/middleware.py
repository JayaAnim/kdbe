from django import utils

from . import models


class AuthenticationMiddleware:
    model = models.WpUsers
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.user = utils.functional.SimpleLazyObject(
                                            lambda: self.model.get_from_request(request))
        return self.get_response(request)
