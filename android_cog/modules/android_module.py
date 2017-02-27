import json
import os

import yaml
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import connectionDone, Factory
from twisted.protocols.basic import LineReceiver
from up.base_started_module import BaseStartedModule
from up.commands.altitude_command import AltitudeCommand
from up.commands.command import BaseCommand
from up.commands.telemetry_command import TelemetryCommand
from up.registrar import UpRegistrar
from up.utils.up_logger import UpLogger

from android_cog.commands.telemetry_command_handler import TelemetryCommandHandler
from android_cog.registrar import Registrar


class AndroidProvider(BaseStartedModule):
    def __init__(self):
        super().__init__()
        self.__connected = False

    def _execute_initialization(self):
        super()._execute_initialization()
        self.__protocol = AndroidProtocol(self)

    def _execute_start(self):
        super()._execute_start()
        port = self.__read_config()
        if port is None:
            self.logger.critical('Port not set. Set it in %s' % Registrar.CONFIG_FILE_NAME)
            return False
        endpoint = TCP4ServerEndpoint(reactor, port)
        endpoint.listen(AndroidProtocolFactory(self.__protocol))
        self.__telemetry_handle = self.up.command_executor.register_command(TelemetryCommand.NAME,
                                                                            TelemetryCommandHandler(self))
        return True

    def _execute_stop(self):
        super()._execute_stop()

    def send_data(self, data):
        if self.__protocol.transport:
            reactor.callFromThread(self.__protocol.sendLine, data)
        else:
            self.__protocol.enqueue(data)

    def load(self):
        return True

    def client_connected(self, connected):
        self.__connected = connected

    def execute_command(self, command):
        self.up.command_executor.execute_command(command)

    @property
    def telemetry_content(self):
        return {
            'android': {
                'connected': self.connected
            }
        }

    @staticmethod
    def __read_config():
        config_path = os.path.join(os.getcwd(), UpRegistrar.CONFIG_PATH, Registrar.CONFIG_FILE_NAME)
        port = None
        if os.path.isfile(config_path):
            with open(config_path) as f:
                config = yaml.load(f)
                port = config.get(Registrar.PORT_KEY, None)
        return port

    @property
    def connected(self):
        return self.__connected


class AndroidProtocol(LineReceiver):
    def __init__(self, callbacks):
        super().__init__()
        self.delimiter = bytes([10])
        self.__logger = UpLogger.get_logger()
        self.__callbacks = callbacks
        self.__queue = []

    def enqueue(self, data):
        self.__queue.append(data)

    def rawDataReceived(self, data):
        self.__logger.debug("Raw data received {}".format(data))

    def lineReceived(self, line):
        if not bytes(AltitudeCommand.NAME, 'utf-8') in line:
            self.__logger.debug("Data received {}".format(line))
        try:
            parsed_data = json.loads(line.decode('utf-8'))
            self.__callbacks.execute_command(BaseCommand.from_json(parsed_data))
        except json.decoder.JSONDecodeError as e:
            self.__logger.error("Invalid data received.\n\tData were {}.\n\tException risen is {}".format(line, e))
        except Exception as e:
            self.__logger.critical(
                "Exception occurred during data processing.\n\tData were {}.\n\tException risen is {}".format(line, e))

    def connectionMade(self):
        """
        If enqueued data for the Android exists, sends the data and clears the queue
        :return: None
        """
        self.__logger.info("Connection from {} opened".format(self.transport.client[0]))
        self.__callbacks.client_connected(True)
        for data in self.__queue:
            self.sendLine(data)
        self.__queue.clear()

    def connectionLost(self, reason=connectionDone):
        self.__logger.warning("Connection lost")
        self.__callbacks.client_connected(False)


class AndroidProtocolFactory(Factory):
    def __init__(self, protocol):
        super().__init__()
        self.__protocol = protocol

    def buildProtocol(self, addr):
        return self.__protocol
