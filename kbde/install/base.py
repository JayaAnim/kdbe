from . import apt_installer


class Installer(apt_installer.Installer):
    package_names = [
        "tree",
        "parallel",
        "gettext",
        "vim",
        "git",
        "wget",
        "htop",
    ]
