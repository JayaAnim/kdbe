from setuptools import setup, find_packages

setup(name="kbde",
      version="9",
      url="https://gitlab.com/kbGit/kbde",
      author="kbuilds, LLC",
      author_email="k@kbuilds.com",
      description="Development environment library. Foundational python library.",
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        "requests==2.21.0",
        ],
      )
