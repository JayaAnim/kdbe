from . import base


class PythonAptRepo(base.AptRepositoryAdded):
    repository_uri = "ppa:deadsnakes/ppa"


class BasePython3(base.AptInstalled):
    package_names = [
        "build-essential",
        "python3-dev",
    ]
    dependencies = [
        PythonAptRepo,
    ]


class Python_3_6(base.AptInstalled):
    package_names = [
        "python3.6",
        "python3.6-venv",
    ]
    dependencies = [
        BasePython3,
    ]


class Python_3_7(base.AptInstalled):
    package_names = [
        "python3.7",
        "python3.7-venv",
    ]
    dependencies = [
        BasePython3,
    ]


class Python_3_8(base.AptInstalled):
    package_names = [
        "python3.8",
        "python3.8-venv",
    ]
    dependencies = [
        BasePython3,
    ]
