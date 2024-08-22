from os import path

from setuptools import find_packages, setup

install_requires = [
    "numpy",
    "pyyaml",
    "pymunk>=6.0.0",
    "scikit-image",
    "pillow",
    "pytest",
    "matplotlib",
    "arcade",
    "tqdm",
    "gymnasium",
]

test_requires = [
    "flake8",
    "pytest",
    "pytest-cov",
    "pytest-env",
    "pytest-sugar",
    "pylint",
]


dev_requires = [
    "pre-commit",
    "ipdb",
]


# read the contents of the README file

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="spg",
    version="0.1.9",
    description="Simulator for Reinforcement Learning",
    author="Michael Garcia Ortiz",
    author_email="michael.garcia.ortiz@gmail.com",
    packages=find_packages(where="."),
    package_dir={"": "."},
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        "test": test_requires,
        "dev": dev_requires,
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
)
