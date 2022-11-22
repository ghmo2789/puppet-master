from control_server.src.middleware.udp_server import UdpServer


class UdpControlListener:
    def __init__(self, port, host='0.0.0.0', buffer_size=1024):
        self.udp_server = UdpServer(
            port=port,
            host=host,
            buffer_size=buffer_size
        )

        