import importlib


def import_class_from_string(class_string):
    split_class_string = class_string.split(".")
    module_string = ".".join(split_class_string[:-1])
    module = importlib.import_module(module_string)

    return getattr(module, split_class_string[-1])
