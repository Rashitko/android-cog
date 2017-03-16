from up.registrar import UpRegistrar


class Registrar(UpRegistrar):
    CONFIG_FILE_NAME = 'android.yml'
    PORT_KEY = 'general port'
    ORIENTATION_PORT_KEY = 'orientation port'
    STOP_KEY = 'stop if orientation connection is lost'
    STOP_DELAY_KEY = 'stop delay (s)'
    ONBOARD_FORWARD_KEY = 'forward interval for onboard device (ms)'

    CONFIG_TEMPLATE = """\
%s: 50001
%s: 50000
%s: True
%s: 10
%s: 500
""" % (PORT_KEY, ORIENTATION_PORT_KEY, STOP_KEY, STOP_DELAY_KEY, ONBOARD_FORWARD_KEY)

    def __init__(self):
        super().__init__('android_cog')

    def register(self):
        external_modules = self._load_external_modules()
        if external_modules is not None:
            self._register_modules_from_file()
            self._create_config(self.CONFIG_FILE_NAME, self.CONFIG_TEMPLATE)
        return True
