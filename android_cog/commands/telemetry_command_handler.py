from up.commands.command import BaseCommandHandler


class TelemetryCommandHandler(BaseCommandHandler):

    def __init__(self, android_provider):
        super().__init__()
        self.__android_provider = android_provider

    def run_action(self, command):
        super().run_action(command)
        self.android_provider.send_data(command.serialize())

    @property
    def android_provider(self):
        return self.__android_provider