import socket
import traceback
from threading import Thread
from typing import Any

from decouple import config

from control_server.src.middleware.event import Event
from control_server.src.middleware.events.udp_receive_event import UdpReceiveEvent


class UdpServer:
    """
    A UDP server, that listens for UDP messages, and, upon receiving one, fires
    an event.
    """
    def __init__(self, port, host='0.0.0.0', buffer_size=1024):
        self.port = port
        self.host = host
        self.buffer_size = buffer_size
        self.listen_thread: Thread | None = None
        self.socket_thread: Thread | None = None
        self.sock: socket.socket | None = None
        self.is_listening = False
        self.receive_event: Event[UdpReceiveEvent] = Event()

    def __enter__(self):
        """
        Allows the use of the 'with' statement. Starts the UDP server.
        :return:
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Allows the use of the 'with' statement. Stops the UDP server.
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.stop()

    def bind(self) -> socket.socket:
        """
        Binds the UDP server to the specified port and host.
        :return:
        """
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        self.sock.settimeout(config(
            'UDP_SERVER_SOCKET_TIMEOUT',
            cast=float,
            default=1
        ))

        self.sock.bind((self.host, self.port))
        return self.sock

    def _do_listen(self):
        """
        Listens for UDP messages.
        :return:
        """
        self.is_listening = True
        while self.is_listening:
            current_socket = self.bind()
            if self._receive(current_socket):
                # Signal was received to exit
                break

        self.sock = None

    def _receive(self, with_socket: socket):
        """
        Receives a UDP message using a given socket.
        :param with_socket: The socket to receive from, and to possibly send to.
        :return: True if the socket was closed, False otherwise.
        """
        try:
            data, addr = with_socket.recvfrom(self.buffer_size)

            if not self.is_listening:
                return True

            response = self._handle_receive(data, addr)
            if response is not None:
                with_socket.sendto(response, addr)

            with_socket.close()
            return False
        except OSError as e:
            if self.is_listening:
                print(f'Error receiving data, perhaps listening socket '
                      f'was closed?')
                traceback.print_exc()

            if with_socket is not None:
                with_socket.close()

            return False

    def _handle_receive(self, data: bytes, address: Any) -> bytes:
        """
        Handles a received UDP message.
        :param data: The data received within the UDP message.
        :param address: The address of the sender of the UDP message
        :return: A response to send back to the sender of the UDP message, if
        any. Otherwise, None.
        """
        event_data = UdpReceiveEvent(data, address)
        self.receive_event(event_data)
        return event_data.response if event_data.do_respond else None

    # def _init_socket_listener(self):
        # self.sock.listen()

    def listen(self):
        """
        Starts listening for UDP messages on a new thread.
        :return:
        """
        if self.listen_thread is None:
            # self.socket_thread = Thread(
            #     target=self._init_socket_listener,
            # )

            self.listen_thread = Thread(
                target=self._do_listen,
                args=[]
            )

        # self.socket_thread.start()
        self.listen_thread.start()

    def start(self):
        """
        Bind the UDP server to the address and port, and starts listening for
        UDP messages.
        :return:
        """
        # self.bind()
        self.listen()

    def close(self):
        """
        Closes the UDP servers socket, if it is open.
        :return:
        """
        self.sock.shutdown(socket.SHUT_WR)
        self.sock.close()

    def stop(self):
        """
        Stops listening for UDP messages, and closes the UDP servers socket, if
        it is open.
        :return:
        """
        if self.is_listening is not None:
            self.is_listening = False
            self.sock.close()

            while self.sock is not None:
                pass

        # if self.sock is not None:
        #     self.close()
        #     self.sock = None
