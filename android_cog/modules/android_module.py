from up.base_started_module import BaseStartedModule


class AndroidProvider(BaseStartedModule):
    def _execute_start(self):
        super()._execute_start()
        return True

    def _execute_stop(self):
        super()._execute_stop()