from control_server.src.middleware.messages.generic_message import \
    GenericMessage


class MessageReceivedEvent:
    """
    Event that is fired when a generic message is received
    """
    def __init__(self, address: str, message: GenericMessage):
        self.message = message
        self.address = address
