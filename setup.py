import os

import yaml
from setuptools import setup
from setuptools.command.install import install

setup(
    name='android_cog',
    version='0.1',
    packages=['android_cog', 'android_cog.modules', 'android_cog.commands'],
    url='https://github.com/Rashitko/android-cog',
    download_url='https://github.com/Rashitko/android-cog/master/tarball/',
    license='MIT',
    author='Michal Raska',
    author_email='michal.raska@gmail.com',
    description='',
    install_requires=['up', 'pyyaml', 'twisted'],
)
