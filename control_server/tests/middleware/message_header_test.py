from typing import List, Tuple, Dict, Any

import pytest

from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.tests.utils.header_utils import HeaderUtils

datasets: List[Tuple[bytes, Dict[str, Any]]] = [
    (
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        {
            'message_length': 0,
            'status_code': 0,
            'url_length': 0,
            'body_length': 0,
            'headers_length': 0
        }
    ),
    (
        b'\x00\x01\x02\x00\x03\x00\x04\x00\x05',
        {
            'message_length': 1,
            'status_code': 2,
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
    for byte_arr, data_dict in datasets:
        utils.assert_read(
            data=byte_arr,
            expected=data_dict
        )


def test_write(utils: HeaderUtils):
    for byte_arr, data_dict in datasets:
        utils.assert_write(
            expected=byte_arr,
            data=data_dict
        )


def test_read_write(utils: HeaderUtils):
    for _, data_dict in datasets:
        utils.assert_read_write(data=data_dict)

# def test_message_header_parse():
#     # Format:        H       B   H       H       H
#     sample_bytes = b'\x00\x01\x02\x00\x03\x00\x04\x00\x05'
#     header = MessageHeader(data=sample_bytes)
#     assert header.message_length == 1
#     assert header.status_code == 2
#     assert header.url_length == 3
#     assert header.body_length == 4
#     assert header.headers_length == 5
#
#
# def test_message_header_parse():
#     # Format:        H       B   H       H       H
#     sample_bytes = b'\x00\x01\x02\x00\x03\x00\x04\x00\x05'
#     header = MessageHeader()
#     header.message_length = 1
#     header.status_code = 2
#     header.url_length = 3
#     header.body_length = 4
#     header.headers_length = 5
#     assert header.to_bytes() == sample_bytes
#
#
# def test_message_header_parse():
#     # Format:        H       B   H       H       H
#     sample_bytes = b'\x00\x01\x02\x00\x03\x00\x04\x00\x05'
#     header = MessageHeader()
#     header.message_length = 1
#     header.status_code = 2
#     header.url_length = 3
#     header.body_length = 4
#     header.headers_length = 5
#     assert header.to_bytes() == sample_bytes
