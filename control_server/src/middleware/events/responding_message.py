from control_server.src.middleware.events.ip_message import IpMessage


class RespondingMessage(IpMessage):
    """
    A message that has support for sending a response
    """
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

    def set_response(self, value: bytes):
        self.response = value

    @property
    def do_respond(self) -> bool:
        return self._do_respond
