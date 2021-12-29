from . import base


class SudoNoPassword(base.LineInFile):
    file_path = "/etc/sudoers"
    file_line = "%sudo ALL=(ALL) NOPASSWD:ALL"
