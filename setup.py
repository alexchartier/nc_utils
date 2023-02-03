import os
from setuptools import setup, find_packages


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="nc_utils",
    version="0.0.0",
    author="",
    author_email="",
    description=(""),
    license="",
    keywords="",
    url="",
    packages=find_packages(),
    long_description=read('README.md'),
)
