import os
import struct
import time
from threading import Thread

import yaml
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory, connectionDone
from up.base_started_module import BaseStartedModule
from up.commands.stop_command import BaseStopCommand
from up.modules.base_orientation_provider import BaseOrientationProvider
from up.registrar import UpRegistrar

from android_cog.modules.android_module import AndroidProvider
from android_cog.registrar import Registrar


class AndroidOrientationProvider(BaseStartedModule):
    LOAD_ORDER = AndroidProvider.LOAD_ORDER + 1

    DEFAULT_STOP_DELAY = 10

    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__protocol = None
        self.__orientation_provider = None
        self.__connected = False

    def _execute_initialization(self):
        super()._execute_initialization()
        self.__port, self.__stop_on_conn_lost, self.__stop_delay = self.__read_config()
        if self.__port is None:
            raise ValueError("Orientation port not set. Set it in the %s config under key '%s'" % (Registrar.CONFIG_FILE_NAME, Registrar.ORIENTATION_PORT_KEY))
        self.__protocol = AndroidOrientationProtocol(self)
        self.__orientation_provider = self.up.get_module(BaseOrientationProvider)
        if self.__orientation_provider is None:
            self.logger.critical("Orientation Provider not available")
            raise ValueError("Orientation Provider not available")

    def _execute_start(self):
        orientation_endpoint = TCP4ServerEndpoint(reactor, self.__port)
        orientation_endpoint.listen(AndroidOrientationProtocolFactory(self.__protocol))
        return True

    def _execute_stop(self):
        super()._execute_stop()

    def on_orientation_changed(self, roll, pitch, yaw):
        self.__orientation_provider.yaw = yaw
        self.__orientation_provider.pitch = pitch
        self.__orientation_provider.roll = roll

    def on_connection_made(self):
        self.__connected = True
        self.logger.info("Receiving orientation from Android")

    def on_connection_lost(self):
        self.__connected = False
        self.logger.warning("Android connection lost")
        if self.__stop_on_conn_lost:
            Thread(target=self.__stop_countdown, name="STOP_COUNTDOWN_THREAD").start()

    def __stop_countdown(self):
        for i in range(0, self.__stop_delay):
            if self.__connected:
                return
            self.logger.warning("Shutting down in %ss unless connection is restored" % (10 - i))
            time.sleep(1)
        self.up.command_executor.execute_command(BaseStopCommand())

    def __read_config(self):
        config_path = os.path.join(os.getcwd(), UpRegistrar.CONFIG_PATH, Registrar.CONFIG_FILE_NAME)
        port = None
        stop = True
        stop_delay = self.DEFAULT_STOP_DELAY
        if os.path.isfile(config_path):
            with open(config_path) as f:
                config = yaml.load(f)
                port = config.get(Registrar.ORIENTATION_PORT_KEY, None)
                stop = config.get(Registrar.STOP_KEY, True)
                stop_delay = config.get(Registrar.STOP_DELAY_KEY, 10)
        return port, stop, stop_delay

    def load(self):
        return True


class AndroidOrientationProtocol(Protocol):
    FLOAT_SIZE = 4
    ORIENTATION_DATA_COMPONENTS = 6

    def __init__(self, callbacks):
        self.__callbacks = callbacks
        self.__recv_buffer = bytes()

    def dataReceived(self, data):
        self.__recv_buffer += data
        payload_size = self.FLOAT_SIZE * self.ORIENTATION_DATA_COMPONENTS
        while len(self.__recv_buffer) >= payload_size:
            processable = self.__recv_buffer[:payload_size]
            if len(processable) == payload_size:
                self.__recv_buffer = self.__recv_buffer[payload_size:]
                roll, pitch, yaw, roll_rate, pitch_rate, yaw_rate = struct.unpack("!ffffff", processable)
                self.__callbacks.on_orientation_changed(roll, pitch, yaw)

    def connectionMade(self):
        super().connectionMade()
        self.__callbacks.on_connection_made()

    def connectionLost(self, reason=connectionDone):
        super().connectionLost(reason)
        self.__callbacks.on_connection_lost()


class AndroidOrientationProtocolFactory(Factory):
    def __init__(self, protocol):
        self.__protocol = protocol

    def buildProtocol(self, addr):
        return self.__protocol
