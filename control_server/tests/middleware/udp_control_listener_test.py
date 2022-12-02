from typing import Generic, TypeVar

import pytest
from decouple import config

from control_server.src.middleware.events.message_received_event import \
    MessageReceivedEvent
from control_server.src.middleware.udp_control_listener import \
    UdpControlListener
from control_server.tests.utils.udp_utils import send_bytes

url_data = 'A'
body_data = 'B'
header_data = 'C'

message_bytes = b'\x00\x0C\xFF\x00\x01\x00\x01\x00\x01' + \
                url_data.encode('utf-8') + \
                body_data.encode('utf-8') + \
                header_data.encode('utf-8')

host = '127.0.0.1'
port = 36652

T = TypeVar('T')


class ResultContainer(Generic[T]):
    """
    Class to hold results received from another thread
    """
    def __init__(self):
        self.result: T = None

    def set_result(self, result: T):
        self.result = result

    def get_result(self) -> T:
        return self.result


def get_control_listener():
    """
    Instantiates a control server UDP listener
    :return: The control server UDP listener
    """
    return UdpControlListener(port=port)


def test_valid_message():
    """
    Tests that a valid message is received correctly
    :return:
    """
    if config('CI', default=False, cast=bool):
        pytest.skip('Skipping UDP tests on CI')

    rc: ResultContainer[MessageReceivedEvent] = ResultContainer()
    with get_control_listener() as listener:
        listener.message_received += lambda event: rc.set_result(event)

        send_bytes(
            data=message_bytes,
            host=host,
            port=port,
            response_length=0
        )

        while rc.result is None:
            pass

    _assert_response(rc.get_result())


def _assert_response(event: MessageReceivedEvent):
    """
    Asserts that the response is correct
    :param event:
    :return:
    """
    assert event.message.url == url_data
    assert event.message.body == body_data
    assert event.message.headers == header_data
    assert event.message.url_length == len(url_data)
    assert event.message.body_length == len(body_data)
    assert event.message.headers_length == len(header_data)
