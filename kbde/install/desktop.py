from . import apt_installer


class Installer(apt_installer.Installer):
    package_names = [
        "ubuntu-gnome-desktop",
        "vlc",
    ]
