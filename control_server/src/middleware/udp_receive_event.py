from typing import Any


class UdpReceiveEvent:
    def __init__(self, data: bytes, address: Any):
        self._data: bytes = data
        self._address: Any = address
        self._response: bytes | None = None
        self.do_respond: bool = False

    @property
    def data(self):
        return self.data

    @property
    def address(self):
        return self._address

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value: bytes):
        self._response = value
        self.do_respond = True
