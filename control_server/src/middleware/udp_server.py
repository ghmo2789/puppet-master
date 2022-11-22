import socket
from threading import Thread
from typing import Any

from control_server.src.middleware.event import Event
from control_server.src.middleware.udp_receive_event import UdpReceiveEvent


class UdpServer:
    def __init__(self, port, host='0.0.0.0', buffer_size=1024):
        self.port = port
        self.host = host
        self.buffer_size = buffer_size
        self.listen_thread: Thread | None = None
        self.sock: socket.socket | None = None
        self.is_listening = False
        self.receive_event = Event()

    def bind(self):
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        self.sock.bind((self.host, self.port))

    def _do_listen(self):
        current_socket = self.sock
        self.is_listening = True
        while self.is_listening:
            data, addr = current_socket.recvfrom(self.buffer_size)

            if not self.is_listening:
                break

            response = self._handle_receive(data, addr)
            if response is not None:
                current_socket.sendto(response, addr)

    def _handle_receive(self, data: bytes, address: Any) -> bytes:
        event_data = UdpReceiveEvent(data, address)
        self.receive_event(event_data)
        return event_data.response if event_data.do_respond else None

    def listen(self):
        if self.listen_thread is None:
            self.listen_thread = Thread(
                target=self._do_listen,
                args=[]
            )

        self.listen_thread.start()

    def start(self):
        self.bind()
        self.listen()

    def close(self):
        self.sock.shutdown(socket.SHUT_WR)
        self.sock.close()

    def stop(self):
        if self.is_listening is not None:
            self.is_listening = False

        if self.sock is not None:
            self.close()
            self.sock = None
