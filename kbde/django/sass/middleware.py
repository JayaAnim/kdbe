from django.conf import settings
import bs4, sass


class InlineSassMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        document = bs4.BeautifulSoup(response.content, features="html.parser")
        style_tags = document.find_all("style")

        sass_document = ""

        for style_tag in style_tags:
            sass_document += style_tag.string
            style_tag.extract()

        css_style_tag = document.new_tag("style")
        css_style_tag.string = self.get_css(sass_document)
        document.html.head.append(css_style_tag)

        response.content = document.prettify()
        response['Content-Length'] = str(len(response.content))

        return response

    def get_css(self, sass_document):
        if settings.CACHE_INLINE_SASS:
            import memoize

            @memoize.memoize(settings.INLINE_SASS_CACHE_TIMEOUT)
            def compile_sass(sass_document):
                return sass.compile(string=sass_document)

        else:
            def compile_sass(sass_document):
                return sass.compile(string=sass_document)

        return compile_sass(sass_document)
