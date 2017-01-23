from up.registrar import UpRegistrar



class Registrar(UpRegistrar):
    CONFIG_FILE_NAME = 'android.yml'
    PORT_KEY = 'port'

    CONFIG_TEMPLATE = """\
%s: # Place your port here
""" % PORT_KEY

    def __init__(self):
        super().__init__('android_cog')

    def register(self):
        external_modules = self._load_external_modules()
        if external_modules is not None:
            self._register_module('AndroidProvider', 'android_cog.modules.android_module')
            self._register_module('AndroidBatteryProvider', 'android_cog.modules.android_battery_module')
            self._write_external_modules()
        self._create_config(self.CONFIG_FILE_NAME, self.CONFIG_TEMPLATE)
        return True
