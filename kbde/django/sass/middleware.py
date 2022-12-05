from django.conf import settings
from django.core import management
from django.utils import encoding

import sass


class EmbeddedSassMiddleware:
    DEBUG_EMBEDDED_SASS = getattr(
        settings,
        "DEBUG_EMBEDDED_SASS",
        settings.DEBUG,
    )
    CACHE_EMBEDDED_SASS = getattr(
        settings,
        "CACHE_EMBEDDED_SASS",
        not settings.DEBUG,
    )
    EMBEDDED_SASS_CACHE_TIMEOUT = getattr(
        settings,
        "EMBEDDED_SASS_CACHE_TIMEOUT",
        60*60*24,  # 24 hours
    )
    opening_style_tag = "<style sass>"
    ending_style_tag = "</style>"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert isinstance(self.EMBEDDED_SASS_CACHE_TIMEOUT, int)

        response = self.get_response(request)

        if (
            "text/html" not in response.get("content-type", "").lower()
            or not hasattr(response, "content")
        ):
            return response

        content = encoding.smart_str(response.content)

        content, style_tags = self.extract_style_tags(content)

        if "<html>" in content:
            # This is a full-page document
            # Process all sass style tags
            sass_document = self.get_sass(style_tags)

            if sass_document:
                css_document = self.get_css(sass_document)

                style_tag = f"<style>{css_document}</style>"
                insertion_point = "</head>"

                content = content.replace(
                    insertion_point,
                    style_tag + insertion_point,
                )

        response.content = str(content)
        response['content-length'] = str(len(response.content))

        return response

    def extract_style_tags(self, content):
        style_tags = []

        split_content = content.split(self.opening_style_tag)

        if len(split_content) == 1:
            # There are no style tags
            return content, style_tags

        content = [split_content[0]]

        for content_part in split_content[1:]:
            split_content_part = content_part.split(self.ending_style_tag)

            style_tag = split_content_part[0]
            other_content = split_content_part[1:]

            content_part = self.ending_style_tag.join(other_content)

            style_tags.append(style_tag)
            content.append(content_part)

        content = "".join(content)

        return content, style_tags

    def get_css(self, sass_document):

        def compile_sass(string):
            return sass.compile(string=string)

        if self.CACHE_EMBEDDED_SASS:
            import memoize

            memoize_function = memoize.memoize(self.EMBEDDED_SASS_CACHE_TIMEOUT)
            compile_sass = memoize_function(compile_sass)

        if self.DEBUG_EMBEDDED_SASS:
            management.call_command("collectstatic", "--no-input")

        return compile_sass(sass_document)

    def get_sass(self, style_tags):
        sass_strings = []

        for style_tag in style_tags:
            if style_tag not in sass_strings:
                sass_strings.append(style_tag)

        return "\n\n".join(sass_strings)
