from control_server.src.middleware.events.IpMessage import IpMessage


class RespondingMessage(IpMessage):
    def __init__(self, address: str = None):
        super().__init__(address)
        self._response: bytes | None = None
        self._do_respond: bool = False

    @property
    def response(self) -> bytes | None:
        return self._response

    @response.setter
    def response(self, value: bytes):
        self._response = value
        self._do_respond = True

    @property
    def do_respond(self) -> bool:
        return self._do_respond
