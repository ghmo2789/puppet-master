from typing import List, Tuple, Dict, Any

import pytest

from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.tests.utils.header_utils import HeaderUtils

datasets: List[Tuple[bytes, Dict[str, Any]]] = [
    (
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        {
            'message_length': 0,
            'status_code': 0,
            'checksum': 0,
            'url_length': 0,
            'body_length': 0,
            'headers_length': 0
        }
    ),
    (
        b'\x00\x01\x00\x02\x00\xFF\x00\x03\x00\x04\x00\x05',
        {
            'message_length': 1,
            'status_code': 2,
            'checksum': 255,
            'url_length': 3,
            'body_length': 4,
            'headers_length': 5
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
        convertible_creator=lambda: MessageHeader()
    )


def test_read(utils: HeaderUtils):
    """
    Tests that the header can be read from a byte array
    :param utils:
    :return:
    """
    for byte_arr, data_dict in datasets:
        utils.assert_read(
            data=byte_arr,
            expected=data_dict
        )


def test_write(utils: HeaderUtils):
    """
    Tests that the header can be written to a byte array
    :param utils:
    :return:
    """
    for byte_arr, data_dict in datasets:
        utils.assert_write(
            expected=byte_arr,
            data=data_dict
        )


def test_read_write(utils: HeaderUtils):
    """
    Tests that converting a header to bytes and then reading it back results in
    the same header
    :param utils:
    :return:
    """
    for _, data_dict in datasets:
        utils.assert_read_write(data=data_dict)
