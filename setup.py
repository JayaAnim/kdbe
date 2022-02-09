from setuptools import setup, find_packages


setup(
    name="kbde",
    version="90",
    url="https://gitlab.com/kb_git/kbde",
    author="kbuilds, LLC",
    author_email="k@kbuilds.com",
    description="Development environment library. Foundational Python library.",
    packages=find_packages(),
    include_package_data=True,
    scripts=['scripts/kbde_cli.py'],
)
