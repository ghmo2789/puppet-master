import socket

from control_server.src.middleware.compression.compression import Compression
from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.src.middleware.messages.generic_message import \
    GenericMessage
from control_server.src.middleware.obfuscation_key import ObfuscationKey


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

    obfuscation = ObfuscationKey.get_key()
    data = obfuscation.apply(data)

    sock.sendto(data, (host, port))

    response = None
    if buffer_size > 0:
        response, _ = sock.recvfrom(buffer_size)
        response = obfuscation.apply(response)

    sock.close()
    return response


def \
        send_receive_message(
        message: GenericMessage,
        host: str,
        port: int,
        recalculate_checksum: bool = True
) -> GenericMessage:
    """
    Sends bytes to a host and port and returns the response
    :param recalculate_checksum: Whether to recalculate the checksum of the
    message before sending it
    :param message: The message to send
    :param host: The host to send to
    :param port: The port to send to
    :return: The response, if any. None if response_length is 0 or less.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    compression = Compression.get_default()
    data = message.to_bytes(
        compression=compression,
        recalculate_checksum=recalculate_checksum
    )

    obfuscation = ObfuscationKey.get_key()
    data = obfuscation.apply(data)

    sock.sendto(data, (host, port))

    response_bytes, _ = sock.recvfrom(1024)
    response_bytes = obfuscation.apply(response_bytes)
    header = MessageHeader(data=response_bytes)

    header_bytes = response_bytes[:MessageHeader.size()]
    data_bytes = response_bytes[MessageHeader.size():]

    data_bytes = compression.decompress(data_bytes)

    response = GenericMessage(
        message_header=header,
        data=header_bytes + data_bytes
    )

    sock.close()
    return response
