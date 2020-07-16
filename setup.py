from setuptools import setup

setup(
    name='flatland',
    version='0.9',
    description='Flatland for AGI and RL',
    author='Michael Garcia Ortiz',
    author_email='michael.garcia.ortiz@gmail.com',
    packages=['flatland'],  #same as name
    install_requires=[ 'pyyaml',
                       'markdown',
                       'pymunk',
                       'pygame',
                       'opencv-python',
                       'numpy',


      ],
)