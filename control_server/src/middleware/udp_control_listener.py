from control_server.src.middleware.checksum import Checksum
from control_server.src.middleware.compression.compression import Compression
from control_server.src.utils.event import Event
from control_server.src.middleware.events.message_received_event import \
    MessageReceivedEvent
from control_server.src.middleware.generic_message_builder import \
    GenericMessageBuilder
from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.src.middleware.messages.generic_message import \
    GenericMessage
from control_server.src.middleware.events.udp_receive_event import \
    UdpReceiveEvent
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
        self.compression = Compression.read_from_settings()
        self.checksum = Checksum.read_from_settings()

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

    @staticmethod
    def create_error_response(
            error_code: int
    ) -> GenericMessage:
        """
        Creates a GenericMessage with the given error code
        :param error_code: The error code to create a response for
        :return: The response, as a GenericMessage
        """
        return GenericMessageBuilder() \
            .set_status_code(error_code) \
            .set_url('') \
            .set_headers('') \
            .set_body('') \
            .build()

    def _handle_receive_udp_event(self, event: UdpReceiveEvent):
        header = MessageHeader(
            data=event.data
        )

        calculated_checksum = GenericMessage.calculate_data_checksum(
            data=event.data,
            checksum=self.checksum
        )

        if calculated_checksum != header.checksum:
            print(
                f'{event.address} ERR: Checksum mismatch: provided value '
                f'{hex(header.checksum)} differs from actual value '
                f'{hex(calculated_checksum)}'
            )

            event.set_response(
                UdpControlListener.create_error_response(400).to_bytes()
            )

            return

        header_data = event.data[:MessageHeader.size()]
        message_data = event.data[MessageHeader.size():]

        message_data = self.compression.decompress(message_data)

        message = GenericMessage(
            message_header=header,
            data=header_data + message_data
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
