#!/usr/bin/env python3
"""
3 Very simple HTTP server in python for logging requests
4 Usage::
5     ./server.py [<port>]
6 """
import struct
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import argparse
import socket

_LOCAL_IP = '127.0.0.1'
_LOCAL_PORT = 65500
_BUFFER_SIZE = 550

_INIT_CLIENT_KEYS = ['os_name', 'os_version', 'hostname', 'host_user', 'privileges']
_INIT_CLIENT_PATH = '/control/client/init'

_CLIENT_HEADER = 'content-type: application/json'
_TEST_TOKEN = "12345"

_TASK_RESULT_PATH = "/control/client/task/response"
_TASK_PATH = '/control/client/task'
_TEST_TASKS = """[
    {
        "id": "1",
        "data": "ls -al",
        "max_delay": 500,
        "min_delay": 0,
        "name": "terminal"
    },
    {
        "id": "2",
        "data": "echo Hejsan!",
        "max_delay": 1000,
        "min_delay": 100,
        "name": "terminal"
    },
    {
        "id": "3",
        "data": "hejhej",
        "max_delay": 150,
        "min_delay": 0,
        "name": "terminal"
    }         
]"""

_DEMO_TASKS = """[
    {
        "id": "1",
        "data": "ls -al",
        "max_delay": 2000,
        "min_delay": 1000,
        "name": "terminal"
    },
    {
        "id": "2",
        "data": "echo Hejsan!",
        "max_delay": 2000,
        "min_delay": 1000,
        "name": "terminal"
    },
    {
        "id": "3",
        "data": "hejhejhej",
        "max_delay": 1000,
        "min_delay": 0,
        "name": "terminal"
    },
    {
        "id": "4",
        "data": "ping 127.0.0.1",
        "max_delay": 150,
        "min_delay": 0,
        "name": "terminal"
    },
    {
        "id": "5",
        "data": "ping 127.0.0.1",
        "max_delay": 150,
        "min_delay": 0,
        "name": "terminal"
    },
    {
        "id": "6",
        "data": "ping 127.0.0.1",
        "max_delay": 150,
        "min_delay": 0,
        "name": "terminal"
    }      
]"""
_DEMO_TASKS_2 = """[
    {
        "id": "5",
        "data": "4,5,6",
        "max_delay": 0,
        "min_delay": 0,
        "name": "abort"
    }        
]"""

n_gets = 0
demo = True


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_fail_response(self):
        self.send_response(401)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global n_gets, demo
        print("----------------------------------------------------------")
        print(f"Received GET request to {self.path}\n")
        if _TEST_TOKEN in str(self.headers):
            self._set_response()
            if demo:
                message = _DEMO_TASKS if n_gets % 2 == 0 else _DEMO_TASKS_2
            else:
                message = _TEST_TASKS
        else:
            self._set_fail_response()
            message = 'Failed auth'

        print(f'Responding with: {message}')
        self.wfile.write(message.encode('utf-8'))
        n_gets += 1

    def do_POST(self):
        if not (_CLIENT_HEADER in str(self.headers)):
            print(f"Faulty header: {self.headers} vs {_CLIENT_HEADER}")
            self._set_response()
            message = {"FAIL": "TEST"}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return

        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('utf-8')  # <--- Gets the data itself

        print("----------------------------------------------------------")
        print(f"Received POST request to {self.path}\nBody:\n{post_data}\n")  # self.headers

        d = json.loads(post_data)
        if self.path == _INIT_CLIENT_PATH:
            message = {"Authorization": _TEST_TOKEN}
            for k in _INIT_CLIENT_KEYS:
                if k not in d:
                    print(f"{k} not in post body!")
                    message["Authorization"] = 'FAIL'
        elif self.path == _TASK_RESULT_PATH:
            message = ''
        else:
            message = {"Not": "Implemented"}

        print(f'Responding with: {message}')
        self._set_response()
        self.wfile.write(json.dumps(message).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


def udp_init_response():
    body = b'{"Authorization": "12345"}'
    url_len = 0
    req_h_len = 0
    body_len = len(body)
    status_code = 200
    message_len = 9 + url_len + body_len + req_h_len
    header = struct.pack('>HBHHH', message_len, status_code, url_len, body_len, req_h_len)
    mes = header + body
    return mes


def udp_get_commands_response():
    body = _TEST_TASKS.encode()
    url_len = 0
    req_h_len = 0
    body_len = len(body)
    status_code = 200
    message_len = 9 + url_len + body_len + req_h_len
    header = struct.pack('>HBHHH', message_len, status_code, url_len, body_len, req_h_len)
    mes = header + body
    return mes


def run_udp():
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server_socket.bind((_LOCAL_IP, _LOCAL_PORT))
    while True:
        try:
            message, address = server_socket.recvfrom(_BUFFER_SIZE)
            print(f'Message received from {address}:\n{message}')
            message_len, status_code, url_len, body_len, req_h_len = struct.unpack('>HBHHH', message[0:9])
            index = 9
            url = message[index:index + url_len].decode('utf-8')
            index += url_len
            body = message[index:index + body_len].decode('utf-8')
            index += body_len
            req_h = message[index:index + req_h_len].decode('utf-8')

            if _INIT_CLIENT_PATH in url:
                msg = udp_init_response()
                server_socket.sendto(msg, address)
            elif _TASK_PATH in url:
                msg = udp_get_commands_response()
                server_socket.sendto(msg, address)
            if _TASK_RESULT_PATH in url:
                pass

        except KeyboardInterrupt:
            break


def parse_args():
    parser = argparse.ArgumentParser(description="Test server for puppet-master client")
    parser.add_argument('--port',
                        default=8080,
                        type=int,
                        help='What port the server will listen on, if not set, 8080 is default')
    parser.add_argument('--demo',
                        action='store_true',
                        default=False,
                        help='If running in demo mode or not')
    parser.add_argument('--udp',
                        action='store_true',
                        default=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    demo = args.demo
    if args.udp:
        run_udp()
    else:
        run(port=args.port)
