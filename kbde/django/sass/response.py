from django.template import response
from django.conf import settings

import sass


class SassResponse(response.TemplateResponse):
    
    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)

        compile_args = {
            "indented": template.template.name.endswith(".sass"),
        }

        if settings.CACHE_SASS:
            import memoize

            @memoize.memoize(settings.SASS_CACHE_TIMEOUT)
            def compile_sass(string):
                return sass.compile(string=string, **compile_args)

        else:
            def compile_sass(string):
                return sass.compile(string=string, **compile_args)

        return compile_sass(super().rendered_content)
