import struct

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory
from up.base_started_module import BaseStartedModule
from up.modules.base_orientation_provider import BaseOrientationProvider

from android_cog.modules.android_module import AndroidProvider


class AndroidOrientationProvider(BaseStartedModule):
    LOAD_ORDER = AndroidProvider.LOAD_ORDER + 1

    PORT = 50000

    def __init__(self, config=None, silent=False):
        super().__init__(config, silent)
        self.__protocol = None
        self.__orientation_provider = None

    def _execute_initialization(self):
        super()._execute_initialization()
        self.__protocol = AndroidOrientationProtocol(self)
        self.__orientation_provider = self.up.get_module(BaseOrientationProvider)
        if self.__orientation_provider is None:
            self.logger.critical("Orientation Provider not available")
            raise ValueError("Orientation Provider not available")

    def _execute_start(self):
        orientation_endpoint = TCP4ServerEndpoint(reactor, self.PORT)
        orientation_endpoint.listen(AndroidOrientationProtocolFactory(self.__protocol))
        return True

    def _execute_stop(self):
        super()._execute_stop()

    def on_orientation_changed(self, roll, pitch, yaw):
        self.__orientation_provider.yaw = yaw
        self.__orientation_provider.pitch = pitch
        self.__orientation_provider.roll = roll

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


class AndroidOrientationProtocolFactory(Factory):
    def __init__(self, protocol):
        self.__protocol = protocol

    def buildProtocol(self, addr):
        return self.__protocol
