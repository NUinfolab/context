from os.path import expanduser
from setuptools import setup, find_packages 


setup(
    name='context',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'newspaper',
        'numpy',
        'birdy',
    ],
    dependency_links = [
    ],
    test_suite='tests',
)
