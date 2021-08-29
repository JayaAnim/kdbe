from django.conf import settings
from django.core import management
from django.utils import timezone

import bs4, sass, pytz


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


class EmbeddedSassMiddleware:
    debug_embedded_sass = getattr(settings, "DEBUG_EMBEDDED_SASS", settings.DEBUG)
    cache_embedded_sass = getattr(settings, "CACHE_EMBEDDED_SASS", not debug_sass)
    embedded_sass_cache_timeout = getattr(
        settings,
        "EMBEDDED_SASS_CACHE_TIMEOUT",
        60*60*24,  # 24 hours
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert isinstance(self.embedded_sass_cache_timeout, int)

        response = self.get_response(request)

        document = bs4.BeautifulSoup(response.content, features="html.parser")
        sass_document = self.get_sass(document)

        if sass_document:
            css_style_tag = document.new_tag("style")
            css_style_tag.string = self.get_css(sass_document)
            document.html.head.append(css_style_tag)

        response.content = document.prettify()
        response['content-length'] = str(len(response.content))

        return response

    def get_css(self, sass_document):
        if self.cache_embedded_sass:
            import memoize

            @memoize.memoize(self.embedded_sass_cache_timeout)
            def compile_sass(string):
                return sass.compile(string=string)

        else:
            def compile_sass(string):
                return sass.compile(string=string)

        if self.debug_sass:
            management.call_command("collectstatic", "--no-input")

        return compile_sass(sass_document)

    def get_sass(self, document):
        style_tags = document.find_all("style")

        sass_strings = []

        for style_tag in style_tags:
            if style_tag.string not in sass_strings:
                sass_strings.append(style_tag.string)

            style_tag.extract()

        return "\n\n".join(sass_strings)
