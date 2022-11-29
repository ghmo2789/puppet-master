from control_server.src.middleware.messages.generic_message import \
    GenericMessage


class MessageReceivedEvent:
    def __init__(self, message: GenericMessage):
        self.message = message