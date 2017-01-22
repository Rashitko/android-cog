import os

import yaml
from setuptools import setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        upm_install_path = os.environ.get('UPM_INSTALL_PATH', os.getcwd())
        path = os.path.join(upm_install_path, 'external_modules.yml')
        with open(path) as external_mods_file:
            external_mods = yaml.load(external_mods_file)
            if external_mods is None:
                external_mods = {}
        with open(path, 'w+') as external_mods_file:
            external_mods['android_cog'] = {
                'modules': [
                    {'prefix': 'android_cog.modules.android_module', 'class_name': 'AndroidProvider'}
                ],
                'recorders': []
            }
            yaml.dump(external_mods, external_mods_file)
        install.run(self)


setup(
    name='android_cog',
    version='0.1',
    packages=['android_cog', 'android_cog.modules'],
    url='',
    license='',
    author='Michal Raska',
    author_email='michal.raska@gmail.com',
    description='',
    install_requires=['up', 'pyyaml', 'pyserial', 'twisted'],
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostInstallCommand,
    }
)
