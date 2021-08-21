from django.conf import settings
from django.template import loader
from django.core import management

import sass, hashlib


class SassCompiler:
    default_template_names = [
        "sass/page.sass",
        "sass/page.scss",
    ]
    debug_sass = getattr(settings, "DEBUG_SASS", settings.DEBUG)
    cache_sass = getattr(settings, "CACHE_SASS", not debug_sass)
    sass_cache_timeout = getattr(
        settings,
        "SASS_CACHE_TIMEOUT",
        60*60*24,  # 24 hours
    )
    
    def __init__(self, template_names=None):
        if template_names is None:
            template_names = self.default_template_names.copy()

        self.template = loader.select_template(template_names)
        self.indented = self.template.template.name.endswith(".sass")

    def get_css_hash(self, context):
        css = self.get_css(context)
        hasher = hashlib.sha256(css.encode("latin1"))
        return hasher.hexdigest()[:16]
    
    def get_css(self, context):
        """
        Takes sass and returns compiled css
        """
        sass_document = self.get_sass(context)

        compile_args = {
            "indented": self.indented,
        }

        if self.cache_sass:
            # The django-memoize package must be installed
            # https://django-memoize.readthedocs.io/en/latest/
            import memoize

            @memoize.memoize(self.sass_cache_timeout)
            def compile_sass(string):
                return sass.compile(string=string, **compile_args)

        else:
            def compile_sass(string):
                return sass.compile(string=string, **compile_args)

        return compile_sass(sass_document)

    def get_sass(self, context):
        if self.debug_sass:
            management.call_command("collectstatic", "--no-input")

        return self.template.render(context)
