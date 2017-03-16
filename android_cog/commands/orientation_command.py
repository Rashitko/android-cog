from up.commands.command import BaseCommand, BaseCommandHandler


class OrientationCommand(BaseCommand):
    NAME = 'android.orientation'

    def __init__(self):
        super().__init__(OrientationCommand.NAME)

    @staticmethod
    def __create_data(level):
        return {'level': level}


class OrientationCommandHandler(BaseCommandHandler):
    def __init__(self, provider):
        super().__init__()
        self.__provider = provider

    def run_action(self, command):
        pass
