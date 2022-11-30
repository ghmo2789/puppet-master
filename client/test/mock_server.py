#!/usr/bin/env python3
"""
3 Very simple HTTP server in python for logging requests
4 Usage::
5     ./server.py [<port>]
6 """
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

_TASK_RESULT_PATH = "/client/task/result"
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
        "data": "hejhej",
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
        "data": "ping 192.168.1.247",
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


def run_udp():
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server_socket.bind((_LOCAL_IP, _LOCAL_PORT))
    while True:
        try:
            message, address = server_socket.recvfrom(_BUFFER_SIZE)
            print(f'Message received from {address}:\n{message}')
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
