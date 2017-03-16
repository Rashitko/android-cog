import os
import time

import yaml
from up.commands.command import BaseCommandHandler
from up.registrar import UpRegistrar

from android_cog.registrar import Registrar


class TelemetryCommandHandler(BaseCommandHandler):
    def __init__(self, android_provider):
        super().__init__()
        self.__android_provider = android_provider
        self.__prev_send = 0
        self.__forward_interval = self.__read_config()

    def run_action(self, command):
        super().run_action(command)
        now = int(round(time.time() * 1000))
        if now - self.__prev_send > self.__forward_interval:
            self.android_provider.send_data(command.serialize())
            self.__prev_send = now

    def __read_config(self):
        config_path = os.path.join(os.getcwd(), UpRegistrar.CONFIG_PATH, Registrar.CONFIG_FILE_NAME)
        port = None
        if os.path.isfile(config_path):
            with open(config_path) as f:
                config = yaml.load(f)
                port = config.get(Registrar.ONBOARD_FORWARD_KEY, None)
        return port

    @property
    def android_provider(self):
        return self.__android_provider
