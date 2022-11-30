from typing import Any

from control_server.src.middleware.events.responding_message import \
    RespondingMessage


class UdpReceiveEvent(RespondingMessage):
    """
    Event that is fired when a UDP message is received
    """
    def __init__(self, data: bytes, address: Any):
        super().__init__(address)
        self._data: bytes = data

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def address(self) -> str:
        return self._address
