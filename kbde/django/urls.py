from django import urls

import re


def path(url_path, view_class):
    """
    Returns a complete Django path based on just the view_class.
    Overrides template_name based on class name.
    """
    # Path name is the view name
    path_name = view_class.__name__

    # Template name is {module_name}/{path_name}.html
    module_name_list = view_class.__module__.split(".")[:-1]
    module_name = "/".join(module_name_list)
    template_name = f"{module_name}/{path_name}.html"

    if hasattr(view_class, "template_name"):
        as_view_kwargs = {
            "template_name": template_name,
        }
    else:
        as_view_kwargs = {}

    return urls.path(
        url_path,
        view_class.as_view(**as_view_kwargs),
        name=path_name,
    )
