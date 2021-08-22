from django import template


register = template.Library()


@register.inclusion_tag("kbde/django/pwa/meta.html")
def pwa_meta():
    return {}
