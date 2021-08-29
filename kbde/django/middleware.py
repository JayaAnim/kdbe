from django.utils import timezone

import pytz


class TimezoneMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
    
        tz = request.COOKIES.get("kb_tz")
        if tz:
            try:
                timezone.activate(tz)
            except pytz.UnknownTimeZoneError:
                pass
        else:
            timezone.deactivate()

        return self.get_response(request)
