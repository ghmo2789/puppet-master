import socket


def send_bytes(
        data: bytes,
        host: str,
        port: int,
        response_length: int
) -> bytes:
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

    response = None
    if response_length > 0:
        response, _ = sock.recvfrom(response_length)

    sock.close()
    return response
