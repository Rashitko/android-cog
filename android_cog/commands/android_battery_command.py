from up.commands.command import BaseCommand, BaseCommandHandler


class AndroidBatteryCommand(BaseCommand):
    NAME = 'android.battery'

    def __init__(self, level):
        super().__init__(AndroidBatteryCommand.NAME, self.__create_data(level))

    @staticmethod
    def __create_data(level):
        return {'level': level}


class AndroidBatteryCommandHandler(BaseCommandHandler):
    def __init__(self, provider):
        super().__init__()
        self.__provider = provider

    def run_action(self, command):
        if command is None or command.data is None:
            self.logger.error("Cannot run action if command data are None")
            return None
        self.__provider.battery_level = command.data.get('level', None)
        self.logger.debug("Android's battery level {}".format(self.__provider.battery_level))
