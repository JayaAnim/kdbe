from setuptools import setup, find_packages

setup(name="kbde",
      version="0.1",
      url="https://git.kbuilds.com/kbde/kbde",
      author="kbuilds, LLC",
      author_email="k@kbuilds.com",
      description="Development environment library. Foundational python library.",
      install_requires=[
        "requests",
        "openpyxl",
        ],
      packages=find_packages(),
      include_package_data=True,
      )
