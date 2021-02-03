from django import template
from django.core import exceptions
from kbde.import_tools import utils as import_utils


register = template.Library()


@register.filter()
def has_permissions(request, view_name):
    view_class = import_utils.import_class_from_string(view_name)

    view = view_class()
    view.setup(request)

    try:
        view.check_permissions()
    except exceptions.PermissionDenied:
        return False

    return True
