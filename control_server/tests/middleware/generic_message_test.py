from typing import List, Tuple, Dict, Any

import pytest

from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.src.middleware.messages.generic_message import \
    GenericMessage
from control_server.tests.utils.header_utils import HeaderUtils

datasets: List[Tuple[bytes, Dict[str, Any]]] = [
    (
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00AAA',
        {
            'message_length': 0,
            'status_code': 0,
            'url_length': 0,
            'body_length': 0,
            'headers_length': 0,
            'url': b'A',
            'body': b'A',
            'headers': b'A'
        }
    ),
    (
        b'\x00\x01\x02\x00\x03\x00\x04\x00\x05ABC',
        {
            'message_length': 1,
            'status_code': 2,
            'url_length': 3,
            'body_length': 4,
            'headers_length': 5,
            'url': b'A',
            'body': b'B',
            'headers': b'C'
        }
    )
]


@pytest.fixture(scope="class", autouse=True)
def utils():
    """
    Creates header utils for the test class
    :return:
    """
    yield HeaderUtils(
        convertible_creator=lambda: GenericMessage(
            MessageHeader(
                url_length=1,
                body_length=1,
                headers_length=1
            )
        )
    )


def test_read(utils: HeaderUtils):
    for byte_arr, expected_dict in datasets:
        utils.assert_read(
            data=byte_arr,
            expected=expected_dict
        )


def test_write(utils: HeaderUtils):
    for byte_arr, expected_dict in datasets:
        utils.assert_write(
            expected=byte_arr,
            data=expected_dict
        )


def test_read_write(utils: HeaderUtils):
    for _, expected_dict in datasets:
        utils.assert_read_write(
            data=expected_dict
        )
