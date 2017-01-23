from up.base_started_module import BaseStartedModule

from android_cog.commands.android_battery_command import AndroidBatteryCommand, AndroidBatteryCommandHandler
from android_cog.modules.android_module import AndroidProvider


class AndroidBatteryProvider(BaseStartedModule):

    LOAD_ORDER = AndroidProvider.LOAD_ORDER + 1

    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__battery_level = None
        self.__battery_level_handle = None

    def _execute_start(self):
        self.__battery_level_handle = self.up.command_executor.register_command(
            AndroidBatteryCommand.NAME, AndroidBatteryCommandHandler(self)
        )
        return True

    def _execute_stop(self):
        self.up.command_executor.unregister_command(AndroidBatteryCommand.NAME, self.__battery_level_handle)

    def load(self):
        return True

    @property
    def battery_level(self):
        return self.__battery_level

    @battery_level.setter
    def battery_level(self, value):
        self.__battery_level = value
