from control_server.src.middleware.compression.compression import Compression
from control_server.src.middleware.events.udp_receive_event import \
    UdpReceiveEvent
from control_server.src.middleware.messages.generic_message import \
    GenericMessage


class MessageReceivedEvent(UdpReceiveEvent):
    """
    Event that is fired when a generic message is received
    """

    def __init__(self, event: UdpReceiveEvent, message: GenericMessage):
        super().__init__(
            data=event.data,
            address=event.address
        )

        self.message: GenericMessage = message

    def set_message_response(
            self,
            response: GenericMessage,
            compression: Compression = None):
        self.set_response(response.to_bytes(
            compression=compression,
            recalculate_checksum=True
        ))
