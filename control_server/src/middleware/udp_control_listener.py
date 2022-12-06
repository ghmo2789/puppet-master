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

    def start(self):
        """
        Starts the UDP server
        :return:
        """
        self.udp_server.start()
        self.udp_server.await_ready()

    def stop(self):
        """
        Stops the UDP server
        :return:
        """
        self.udp_server.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def _handle_receive_udp_event(self, event: UdpReceiveEvent):
        header = MessageHeader(
            data=event.data
        )
        message = GenericMessage(
            message_header=header,
            data=event.data
        )
        self.receive_message(udp_event=event, message=message)

    def receive_message(
            self,
            udp_event: UdpReceiveEvent,
            message: GenericMessage
    ):
        """
        Called when a message is received. Fires a message_received event.
        :param udp_event: The UDP event, containing the sender's address and
        the data
        :param message: The message parsed from the sender's data
        :return: Nothing
        """
        event = MessageReceivedEvent(
            event=udp_event,
            message=message
        )

        self.message_received(event)

        udp_event.copy_from(event)
