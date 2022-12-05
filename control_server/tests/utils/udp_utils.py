import socket

from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.src.middleware.messages.generic_message import \
    GenericMessage


def send_bytes(
        data: bytes,
        host: str,
        port: int,
        buffer_size: int = 1024
) -> bytes:
    """
    Sends bytes to a host and port and returns the response
    :param data: The data to send
    :param host: The host to send to
    :param port: The port to send to
    :param buffer_size: The length of the response. If 0, no response is
    expected. The method will wait until at least response_length bytes are
    received.
    :return: The response, if any. None if response_length is 0 or less.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    sock.sendto(data, (host, port))

    response = None
    if buffer_size > 0:
        response, _ = sock.recvfrom(buffer_size)

    sock.close()
    return response


def send_bytes_receive_message(
        data: bytes,
        host: str,
        port: int
) -> GenericMessage:
    """
    Sends bytes to a host and port and returns the response
    :param data: The data to send
    :param host: The host to send to
    :param port: The port to send to
    :param response_length: The length of the response. If 0, no response is
    expected. The method will wait until at least response_length bytes are
    received.
    :return: The response, if any. None if response_length is 0 or less.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (host, port))

    header_length = MessageHeader.size()
    response_bytes, _ = sock.recvfrom(1024)
    header = MessageHeader(data=response_bytes)

    response = GenericMessage(
        message_header=header,
        data=response_bytes
    )

    sock.close()
    return response
