import socket
import sys
import traceback
from threading import Thread, Lock
from time import sleep
from typing import Any

from decouple import config

from control_server.src.middleware.event import Event
from control_server.src.middleware.events.udp_receive_event import \
    UdpReceiveEvent


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
        self.is_bind: bool = False
        self.socket_lock = Lock()

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

    def await_ready(self, delay: int = 0.001):
        while not self.is_bind:
            pass

        sleep(delay)

    def bind(self) -> socket.socket:
        """
        Binds the UDP server to the specified port and host.
        :return:
        """
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        timeout = config(
            'UDP_SERVER_SOCKET_TIMEOUT',
            cast=float,
            default=-1
        )

        if timeout > 0:
            self.sock.settimeout(timeout)

        self.sock.bind((self.host, self.port))
        self.is_bind = True
        return self.sock

    def _do_listen(self):
        """
        Listens for UDP messages.
        :return:
        """
        self.is_listening = True
        holds_lock = False
        while self.is_listening:
            self.socket_lock.acquire()
            holds_lock = True

            try:
                self.bind()
                self.socket_lock.release()
                holds_lock = False
                self._receive(self.sock)
            except OSError as e:
                traceback.print_exc()

        self.sock = None

        if holds_lock:
            self.socket_lock.release()
            holds_lock = False

    def _receive(self, with_socket: socket) -> bool:
        """
        Receives a UDP message using a given socket.
        :param with_socket: The socket to receive from, and to possibly send to.
        :return: True if the socket was closed, False otherwise.
        """
        try:
            data, addr = with_socket.recvfrom(self.buffer_size)

            response = self._handle_receive(data, addr)
            if response is not None:
                with_socket.sendto(response, addr)

            with_socket.close()
            return True
        except TimeoutError:
            with_socket.close()
            return False
        except OSError:
            if self.is_listening:
                print('Error receiving data, perhaps listening socket '
                      'was closed?', file=sys.stderr)
                traceback.print_exc()
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
        try:
            event_data = UdpReceiveEvent(data, address)
            self.receive_event(event_data)
            return event_data.response if event_data.do_respond else None
        except Exception as e:
            print(e, file=sys.stderr)
            traceback.print_exc()

    def listen(self):
        """
        Starts listening for UDP messages on a new thread.
        :return:
        """
        if self.listen_thread is None:
            self.listen_thread = Thread(
                target=self._do_listen,
                args=[]
            )

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
        self.is_bind = False
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

            if self.sock is not None:
                # Tell listening thread it's time to stop
                self.socket_lock.acquire()
                self.sock.close()

                # Wait for listening thread to stop
                while self.sock is not None:
                    pass
