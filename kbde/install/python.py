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
        "build-essential",
        "python3-dev",
        "python3-venv",
        "python3-pip",
        "python3-setuptools",
        "python3-wheel",
    ]
