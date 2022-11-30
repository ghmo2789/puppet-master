from control_server.src.middleware.event import Event
from control_server.src.middleware.events.message_received_event import \
    MessageReceivedEvent
from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.src.middleware.messages.generic_message import \
    GenericMessage
from control_server.src.middleware.events.udp_receive_event import UdpReceiveEvent
from control_server.src.middleware.udp_server import UdpServer


class UdpControlListener:
    """
    A listener that listens for UDP control server messages, and, upon receiving
    one, fires an event.
    """
    def __init__(self, port, host='0.0.0.0', buffer_size=1024):
        self.udp_server = UdpServer(
            port=port,
            host=host,
            buffer_size=buffer_size
        )

        self.udp_server.receive_event += self._handle_receive_udp_event
        self.message_received: Event[MessageReceivedEvent] = Event()

    def __enter__(self):
        self.udp_server.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.udp_server.stop()

    def _handle_receive_udp_event(self, event: UdpReceiveEvent):
        header = MessageHeader(
            data=event.data
        )
        message = GenericMessage(
            message_header=header,
            data=event.data
        )
        self.receive_message(address=event.address, message=message)

    def receive_message(self, address: str, message: GenericMessage) -> bytes:
        self.message_received(MessageReceivedEvent(address, message))
        print(f'Received message from {address}:')
        print(f'\tURL: \t{message.url}')
        print(f'\tBody: \t{message.body}')
        print(f'\tHeaders: \t{message.headers}')
        return b'1'
