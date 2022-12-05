from typing import Callable, Generic, TypeVar

import pytest
from decouple import config

from control_server.src.middleware.events.message_received_event import \
    MessageReceivedEvent
from control_server.src.middleware.forwarding_udp_control_listener import \
    ForwardingUdpControlListener
from control_server.src.middleware.generic_message_builder import \
    GenericMessageBuilder
from control_server.src.middleware.http_method import HttpMethod
from control_server.tests.utils.udp_utils import send_bytes, \
    send_bytes_receive_message

host = '127.0.0.1'
port = 36652


def get_control_listener():
    """
    Instantiates a control server UDP listener
    :return: The control server UDP listener
    """
    return ForwardingUdpControlListener(
        port=port,
        api_base_url=config('TEST_FORWARD_TO_HOST'),
        ignore_route_check=True
    )


def test_simple_message():
    """
    Tests that a valid message is received correctly
    :return:
    """
    if config('CI', default=False, cast=bool):
        pytest.skip('Skipping UDP tests on CI')

    with get_control_listener() as listener:
        send_message = GenericMessageBuilder() \
            .set_url('/') \
            .set_body('') \
            .set_headers('') \
            .set_status_code(HttpMethod.GET.get_value()) \
            .build()

        received_message = send_bytes_receive_message(
            data=send_message.to_bytes(),
            host=host,
            port=port
        )

    assert received_message is not None
    assert received_message.status_code == 200
