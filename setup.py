from setuptools import setup, find_packages

setup(
    name='simple_playgrounds',
    version='0.9.14',
    description='Simulator for AGI and RL',
    author='Michael Garcia Ortiz',
    author_email='michael.garcia-ortiz@city.ac.uk',
    packages=[package for package in find_packages()
                if package.startswith('simple_playgrounds')],
    include_package_data=True
)
