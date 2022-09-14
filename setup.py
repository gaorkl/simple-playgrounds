from os import path

from setuptools import find_packages, setup

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

# read the contents of the README file

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="spg",
    version="0.1.0",
    description="Simulator for Reinforcement Learning",
    author="Michael Garcia Ortiz",
    author_email="michael.garcia-ortiz@city.ac.uk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
