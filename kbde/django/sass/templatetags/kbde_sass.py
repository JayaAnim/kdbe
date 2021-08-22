from django import template, urls
from django.conf import settings

from .. import sass


register = template.Library()
SASS_CACHE_BUST = getattr(settings, "SASS_CACHE_BUST", True)


@register.inclusion_tag("kbde/django/sass/stylesheet_tag.html")
def stylesheet_tag(**kwargs):
    keys = sorted(kwargs.keys())

    get_params = [f"{key}={kwargs[key]}" for key in keys]

    if SASS_CACHE_BUST:
        css_hash = sass.SassCompiler().get_css_hash(kwargs)

        get_params.append(str(css_hash))

    stylesheet_url = urls.reverse("sass:Page")

    get_params = "&".join(get_params)

    if get_params:
        stylesheet_url = f"{stylesheet_url}?{get_params}"

    return {
        "stylesheet_url": stylesheet_url,
    }
