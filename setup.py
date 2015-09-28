#!/usr/bin/env python3

"""Setup module."""
from setuptools import setup, find_packages
import os


def read(fname):
    """Read and return the contents of a file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='msr-cli',
    version='0.0.1',
    description='msr-cli - Magnetic stripe card reader command-line utility',
    long_description=read('README.md'),
    author='Kalman Olah',
    author_email='kalman@inuits.eu',
    url='https://github.com/kalmanolah/msr-cli',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyusb==1.0.0b2'
    ],
    entry_points={
        'console_scripts': [
            'msr-cli = msr_cli:main',
        ]
    }
)
