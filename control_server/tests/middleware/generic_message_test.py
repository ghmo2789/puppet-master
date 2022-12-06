from typing import List, Tuple, Dict, Any

import pytest

from control_server.src.middleware.headers.message_header import MessageHeader
from control_server.src.middleware.messages.generic_message import \
    GenericMessage
from control_server.tests.utils.header_utils import HeaderUtils

datasets: List[Tuple[bytes, Dict[str, Any]]] = [
    (
        b'\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01AAA',
        {
            'message_length': 0,
            'status_code': 0,
            'url_length': 1,
            'body_length': 1,
            'headers_length': 1,
            'url': b'A',
            'body': b'A',
            'headers': b'A'
        }
    ),
    (
        b'\x00\x01\x00\x02\x00\x01\x00\x01\x00\x01ABC',
        {
            'message_length': 1,
            'status_code': 2,
            'url_length': 1,
            'body_length': 1,
            'headers_length': 1,
            'url': b'A',
            'body': b'B',
            'headers': b'C'
        }
    ),
    (
        b'\x00s\x00\x00\x00(\x00*\x00\x18http://127.0.0.1:8080/client/task/result' +
        b'{"id":"2","status":0,"result":"Hejsan!\\n"}"Authorization": "12345"',
        {
            'message_length': 115,
            'status_code': 0,
            'url_length': 40,
            'body_length': 42,
            'headers_length': 24,
            'url': b'http://127.0.0.1:8080/client/task/result',
            'body': b'{"id":"2","status":0,"result":"Hejsan!\\n"}',
            'headers': b'"Authorization": "12345"'
        }
    ),
    (
        b'\x00\x9d\x00\x00\x00)\x00k\x00\x00http://127.0.0.1:8080/control/client/' +
        b'init{"os_name":"macOS","os_version":"12.6.1","hostname":"johans-mbp' +
        b'-5","host_user":"johan","privileges":"null"}',
        {
            'message_length': 157,
            'status_code': 0,
            'url_length': 41,
            'body_length': 107,
            'headers_length': 0,
            'url': b'http://127.0.0.1:8080/control/client/init',
            'headers': b'',
            'body': b'{"os_name":"macOS","os_version":"12.6.1",' +
                    b'"hostname":"johans-mbp' +
                    b'-5","host_user":"johan","privileges":"null"}'
        }
    )
]


@pytest.fixture(scope="class", autouse=True)
def utils():
    """
    Creates header utils for the test class
    :return:
    """
    yield get_utils()


def get_utils(
        url_length: int = 1,
        body_length: int = 1,
        headers_length: int = 1) -> HeaderUtils:
    return HeaderUtils(
        convertible_creator=lambda: GenericMessage(
            MessageHeader(
                url_length=url_length,
                body_length=body_length,
                headers_length=headers_length
            )
        )
    )


def test_read(utils: HeaderUtils):
    """
    Tests that the header can be read from a byte array
    :param utils:
    :return:
    """
    for byte_arr, expected_dict in datasets:
        current_utils = get_utils(
            url_length=expected_dict['url_length'],
            body_length=expected_dict['body_length'],
            headers_length=expected_dict['headers_length']
        )

        current_utils.assert_read(
            data=byte_arr,
            expected=expected_dict
        )


def test_write(utils: HeaderUtils):
    """
    Tests that the header can be written to a byte array
    :param utils:
    :return:
    """
    for byte_arr, expected_dict in datasets:
        current_utils = get_utils(
            url_length=expected_dict['url_length'],
            body_length=expected_dict['body_length'],
            headers_length=expected_dict['headers_length']
        )

        current_utils.assert_write(
            expected=byte_arr,
            data=expected_dict
        )


def test_read_write(utils: HeaderUtils):
    """
    Tests that converting the header to bytes and then back results in the same
    header.
    :param utils:
    :return:
    """
    for _, expected_dict in datasets:
        current_utils = get_utils(
            url_length=expected_dict['url_length'],
            body_length=expected_dict['body_length'],
            headers_length=expected_dict['headers_length']
        )

        current_utils.assert_read_write(
            data=expected_dict
        )
