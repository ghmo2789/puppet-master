from control_server.src.middleware.udp_control_listener import \
    UdpControlListener


def get_control_listener():
    return UdpControlListener(port=36652)


def test_valid_message():
    message_bytes = b'\x00\x01\x02\x00\x03\x00\x04\x00\x05ABC'

