from __future__ import annotations
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

    def copy_from(self, other_event: UdpReceiveEvent):
        if other_event.do_respond:
            self.set_response(other_event.response)
