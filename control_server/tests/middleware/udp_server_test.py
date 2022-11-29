import socket

from control_server.src.middleware.events.udp_receive_event import UdpReceiveEvent
from control_server.src.middleware.udp_server import UdpServer


listen_host = '0.0.0.0'
host = '127.0.0.1'
response_data = b'\x01'
port = 36651
buffer_size = 1024

class ResultContainer:
    def __init__(self):
        self.success = False


def get_udp_server():
    return UdpServer(
        host=listen_host,
        port=port,
        buffer_size=buffer_size
    )


def send_bytes(data: bytes) -> bytes:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (host, port))
    response, _ = sock.recvfrom(len(response_data))
    sock.close()
    return response


def handle_udp_response(
        event: UdpReceiveEvent,
        result: ResultContainer):
    result.success = True
    event.response = response_data


def test_udp_server():
    with get_udp_server() as server:
        result = ResultContainer()
        server.receive_event += lambda event: handle_udp_response(event, result)
        response = send_bytes(b'\x00')
        assert response == response_data
        assert result.success
