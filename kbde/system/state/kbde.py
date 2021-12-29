from . import base


class KbdeCliAutocomplete(base.LineInFile):
    file_path = "~/.bashrc"
    file_line = "%sudo ALL=(ALL) NOPASSWD:ALL"
