from django import urls

import re


def path(url_path, view_class):
    """
    Returns a complete Django path based on just the view_class.
    Overrides template_name based on class name.
    """
    # Break view class name into pieces
    split_class_name = [
        s for s in re.split("([A-Z][^A-Z]*)", view_class.__name__) if s
    ]

    # Path name is the view name in snake case
    path_name = "_".join(s.lower() for s in split_class_name)

    # Template name is {module_name}/{path_name}.html
    module_name = view_class.__module__.split(".")[0]
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
