from django import template, urls, http
from django.core import exceptions
from kbde.import_tools import utils as import_utils


register = template.Library()


@register.filter()
def has_permissions(request, view_location):
    """
    Takes a request and view_location.
    The view_location can be a full url, or a path to a view.
    If a URL can not be resolved from view_location, then the view location
    will be used to import the view_class
    """
    view = None

    try:
        # Try resolving the url
        resolver_match = urls.resolve(view_location)
        view_class = resolver_match.func.view_class
        view = view_class()
        view.setup(request, *resolver_match.args, **resolver_match.kwargs)

    except urls.exceptions.Resolver404:

        try:
            # Try importing the url by the view name
            view_class = import_utils.import_class_from_string(view_location)
            view = view_class()
            view.setup(request)
        except import_utils.ImportUtilsException:
            pass

    assert view is not None, (
        f"Could not find view for \"{view_location}\". This must be either a "
        f"resolvable url, or a path to a view (i.e. my_module.MyViewClass)"
    )

    try:
        view.check_permissions()
    except http.Http404:
        assert False, f"Permission check returned 404 for {view_location}"
    except exceptions.PermissionDenied:
        return False

    return True
