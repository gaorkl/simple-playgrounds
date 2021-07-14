from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='simple_playgrounds',
      version='0.9.30',
      description='Simulator for Reinforcement Learning',
      author='Michael Garcia Ortiz',
      author_email='michael.garcia-ortiz@city.ac.uk',
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      include_package_data=True,
      install_requires=requirements)
