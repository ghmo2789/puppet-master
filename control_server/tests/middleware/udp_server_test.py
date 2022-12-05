import socket

import pytest
from decouple import config

from control_server.src.middleware.events.udp_receive_event import \
    UdpReceiveEvent
from control_server.src.middleware.udp_server import UdpServer
from control_server.tests.utils.udp_utils import send_bytes

listen_host = '0.0.0.0'
host = '127.0.0.1'
response_data = b'\x01'
port = 36651
buffer_size = 1024


class ResultContainer:
    """
    Class to hold whether the result was successfully received
    """
    def __init__(self):
        self.success = False


def get_udp_server():
    """
    Instantiates a UDP server
    :return:
    """
    return UdpServer(
        host=listen_host,
        port=port,
        buffer_size=buffer_size
    )


def handle_udp_response(
        event: UdpReceiveEvent,
        result: ResultContainer):
    """
    Handles a UDP response
    :param event: The UDP event to handle
    :param result: The result container to contain wihether the result was
    successfully received
    :return:
    """
    result.success = True
    event.response = response_data


def test_udp_server():
    """
    Tests that the UDP server can receive a message
    :return:
    """
    if config('CI', default=False, cast=bool):
        pytest.skip('Skipping UDP tests on CI')

    with get_udp_server() as server:
        result = ResultContainer()
        server.receive_event += lambda event: handle_udp_response(event, result)
        response = send_bytes(
            data=b'\x00',
            host=host,
            port=port
        )

        assert response == response_data
        assert result.success


def test_udp_server_twice():
    """
    Tests that the UDP server can receive a message
    :return:
    """
    if config('CI', default=False, cast=bool):
        pytest.skip('Skipping UDP tests on CI')

    with get_udp_server() as server:
        result = ResultContainer()
        server.receive_event += lambda event: handle_udp_response(event, result)
        response = send_bytes(
            data=b'\x00',
            host=host,
            port=port
        )

        assert response == response_data
        assert result.success

        result.success = False
        response = send_bytes(
            data=b'\x00',
            host=host,
            port=port
        )

        assert response == response_data
        assert result.success
