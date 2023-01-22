from django.conf import settings
from django.core import management
from django.utils import encoding

import sass


class TagExtractor:
    
    def __init__(self, content):
        self.content = content

    def extract(self, start_tag, end_tag):
        tag_content_list = []

        split_content = self.content.split(start_tag)

        if len(split_content) == 1:
            # There are no matching tags
            return self.content, tag_content_list

        content = [split_content[0]]

        for content_part in split_content[1:]:
            split_content_part = content_part.split(end_tag)

            tag_content = split_content_part[0]
            other_content = split_content_part[1:]
            other_content = end_tag.join(other_content)

            tag_content_list.append(tag_content)
            content.append(other_content)

        content = "".join(content)

        unique_tag_content_list = []

        for tag_content in tag_content_list:
            if tag_content in unique_tag_content_list:
                continue

            unique_tag_content_list.append(tag_content)

        return content, unique_tag_content_list


class MiddlewareBase:

    def __init__(self, get_response):
        self.get_response = get_response


class DebugMiddleware(MiddlewareBase):
    """
    Handles the additional collection of staticfiles on each request
    This is controlled by settings
    """
    DEBUG_EMBEDDED_SASS = getattr(
        settings,
        "DEBUG_EMBEDDED_SASS",
        settings.DEBUG,
    )

    def __call__(self, request):
        response = self.get_response(request)

        if self.DEBUG_EMBEDDED_SASS:
            management.call_command("collectstatic", "--no-input")

        return response


class EmbeddedSassMiddleware(MiddlewareBase):
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
    start_style_tag = "<style sass>"
    end_style_tag = "</style>"

    def __call__(self, request):
        assert isinstance(self.EMBEDDED_SASS_CACHE_TIMEOUT, int)

        response = self.get_response(request)

        if not response.content:
            return response

        if (
            "text/html" not in response.get("content-type", "").lower()
            or not hasattr(response, "content")
        ):
            return response

        content = encoding.smart_str(response.content)

        extractor = TagExtractor(content)
        content, style_tag_content_list = extractor.extract(
            self.start_style_tag,
            self.end_style_tag,
        )

        if "<html" in content:
            # This is a full-page document
            # Process all sass style tags
            sass_document = self.get_sass(style_tag_content_list)

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

    def get_css(self, sass_document):

        def compile_sass(string):
            return sass.compile(string=string)

        if self.CACHE_EMBEDDED_SASS:
            import memoize

            memoize_function = memoize.memoize(
                self.EMBEDDED_SASS_CACHE_TIMEOUT,
            )
            compile_sass = memoize_function(compile_sass)

        return compile_sass(sass_document)

    def get_sass(self, style_tag_content_list):
        sass_strings = []

        for style_tag_content in style_tag_content_list:
            if style_tag_content not in sass_strings:
                sass_strings.append(style_tag_content)

        return "\n\n".join(sass_strings)


class EmbeddedJavascriptMiddleware(MiddlewareBase):
    start_script_tag = "<script>"
    end_script_tag = "</script>"

    def __call__(self, request):
        response = self.get_response(request)

        if not response.content:
            return response

        if (
            "text/html" not in response.get("content-type", "").lower()
            or not hasattr(response, "content")
        ):
            return response

        content = encoding.smart_str(response.content)

        extractor = TagExtractor(content)
        content, script_tag_content_list = extractor.extract(
            self.start_script_tag,
            self.end_script_tag,
        )

        script = "\n\n".join(script_tag_content_list)
        script_tag = f"<script>{script}</script>"

        if "<body" in content:
            # Append to the bottom of the body
            insertion_point = "</body>"

            content = content.replace(
                insertion_point,
                script_tag + insertion_point,
            )

        else:
            # Append to the bootom of the document
            content = content + script_tag

        response.content = str(content)
        response['content-length'] = str(len(response.content))

        return response
