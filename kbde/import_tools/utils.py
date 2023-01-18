import importlib


class ImportUtilsException(Exception):
    pass


def import_class_from_string(class_string):
    split_class_string = class_string.split(".")
    module_string = ".".join(split_class_string[:-1])

    if not module_string:
        raise ImportUtilsException(
            f"The given string to import, {class_string}, did not contain a "
            f"module and a class, i.e. my_module.MyClass"
        )

    module = importlib.import_module(module_string)

    return getattr(module, split_class_string[-1])
