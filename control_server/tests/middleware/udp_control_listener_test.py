from typing import Generic, TypeVar, Callable

import pytest
from decouple import config

from control_server.src.middleware.events.message_received_event import \
    MessageReceivedEvent
from control_server.src.middleware.generic_message_builder import \
    GenericMessageBuilder
from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.src.middleware.messages.generic_message import \
    GenericMessage
from control_server.src.middleware.obfuscation_key import StaticObfuscationKey
from control_server.src.middleware.udp_control_listener import \
    UdpControlListener
from control_server.tests.utils.udp_utils import send_bytes

url_data = 'A'
body_data = 'B'
header_data = 'C'

message_bytes = \
    b'\x00\x0C\x00\xFF\x99\x90\x00\x01\x00\x01\x00\x01' + \
    url_data.encode('utf-8') + \
    body_data.encode('utf-8') + \
    header_data.encode('utf-8')

message_bytes_wrong_checksum = \
    b'\x00\x0C\x00\xFF\x99\x91\x00\x01\x00\x01\x00\x01' + \
    url_data.encode('utf-8') + \
    body_data.encode('utf-8') + \
    header_data.encode('utf-8')

host = '127.0.0.1'
port = 36652

T = TypeVar('T')

sample_message = GenericMessageBuilder() \
    .set_url(url_data) \
    .set_body(body_data) \
    .set_headers(header_data) \
    .set_status_code(200) \
    .build()


class ResultContainer(Generic[T]):
    """
    Class to hold results received from another thread
    """

    def __init__(self, responder: Callable[[T], None] = None):
        self.result: T = None
        self.response_validator = responder

    def set_result(self, result: T):
        self.result = result

        if self.response_validator is not None:
            self.response_validator(self.result)

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
            buffer_size=0
        )

    _assert_response(rc.get_result().message)


def test_wrong_checksum():
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
            data=message_bytes_wrong_checksum,
            host=host,
            port=port,
            buffer_size=0
        )

    assert rc.get_result() is None


def test_valid_message_with_response():
    """
    Tests that a valid message is received correctly
    :return:
    """
    if config('CI', default=False, cast=bool):
        pytest.skip('Skipping UDP tests on CI')

    rc: ResultContainer[MessageReceivedEvent] = ResultContainer(
        responder=lambda event: _set_response(event)
    )

    response: GenericMessage | None = None

    with get_control_listener() as listener:
        listener.message_received += lambda event: rc.set_result(event)

        response_bytes = send_bytes(
            data=sample_message.to_bytes(),
            host=host,
            port=port,
            buffer_size=sample_message.message_length
        )

        header = MessageHeader(
            data=response_bytes
        )

        response = GenericMessage(
            message_header=header,
            data=response_bytes
        )

        while rc.result is None:
            pass

    _assert_response(response)
    _assert_response(rc.get_result().message)


def test_obfuscated_valid_message():
    with StaticObfuscationKey():
        test_valid_message()


def test_obfuscated_valid_message_with_response():
    with StaticObfuscationKey():
        test_valid_message_with_response()


def _set_response(event: MessageReceivedEvent):
    """
    Sets the response
    :param event:
    :return:
    """
    event.set_message_response(sample_message)


def _assert_response(message: GenericMessage):
    """
    Asserts that the response is correct
    :param message:
    :return:
    """
    assert message.url == url_data
    assert message.body == body_data
    assert message.headers == header_data

    # Strings are all ASCII, so length should match byte length
    assert message.url_length == len(url_data)
    assert message.body_length == len(body_data)
    assert message.headers_length == len(header_data)
