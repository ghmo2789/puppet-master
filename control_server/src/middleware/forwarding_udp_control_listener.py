import json
import sys
import traceback
from datetime import datetime
from json import JSONDecodeError
from typing import Callable
from urllib.parse import urlparse

import requests as requests

from control_server.src.middleware.events.message_received_event import \
    MessageReceivedEvent
from control_server.src.middleware.generic_message_builder import \
    GenericMessageBuilder
from control_server.src.middleware.http_method import HttpMethod
from control_server.src.middleware.messages.generic_message import \
    GenericMessage
from control_server.src.middleware.udp_control_listener import \
    UdpControlListener


class ForwardingUdpControlListener(UdpControlListener):
    """
    A listener that listens for UDP messages and forwards them to a given
    HTTP API endpoint. The response is then sent back to the sender.
    """

    def __init__(
            self,
            api_base_url: str,
            port,
            route_validator: Callable[[str], bool] = None,
            host='0.0.0.0',
            buffer_size=1024,
            ignore_route_check: bool = False
    ):
        super().__init__(
            port=port,
            host=host,
            buffer_size=buffer_size
        )

        self.route_validator: Callable[[str], bool] = route_validator
        self.message_received += self._handle_message_received
        self.api_base_url: str = api_base_url
        self.ignore_route_check: bool = ignore_route_check

        if route_validator is None:
            if not self.ignore_route_check:
                raise Exception('No route validator provided')
            self.route_validator = lambda x: True

    @staticmethod
    def create_message_response(
            response: requests.Response,
            request: GenericMessage
    ) -> GenericMessage:
        """
        Creates a message response from a request GenericMessage and the web
        APIs response
        :param response: The web APIs response
        :param request: The request GenericMessage
        :return: The response, as a GenericMessage
        """
        return GenericMessageBuilder() \
            .set_status_code(response.status_code) \
            .set_url('') \
            .set_headers('') \
            .set_body(response.content.decode('utf-8')) \
            .build()

    @staticmethod
    def create_error_response(
            error_code: int
    ) -> GenericMessage:
        """
        Creates a GenericMessage with the given error code
        :param error_code: The error code to create a response for
        :return: The response, as a GenericMessage
        """
        return GenericMessageBuilder() \
            .set_status_code(error_code) \
            .set_url('') \
            .set_headers('') \
            .set_body('') \
            .build()

    def _handle_message_received(self, event: MessageReceivedEvent):
        """
        Handles a received message by forwarding it and potentially replying.
        :param event: The event to handle
        :return: Nothing
        """
        url_path = urlparse(event.message.url).path
        sender_ip, sender_port = event.address
        result_status = 500

        try:
            if not self.ignore_route_check and \
                    (url_path is None or not self.route_validator(url_path)):
                raise Exception(
                    'No valid route found for url: ' + (url_path or 'None')
                )

            message = event.message
            target_url = self.api_base_url + message.url
            headers = ForwardingUdpControlListener.get_headers(message)

            forward_header_name = 'X-Forwarded-For'
            forward_header = headers[forward_header_name] + ', ' \
                if forward_header_name in headers else \
                sender_ip

            headers[forward_header_name] = forward_header

            handlers = {
                HttpMethod.GET: lambda request: requests.get(
                    url=target_url,
                    headers=headers
                ),
                HttpMethod.POST: lambda request: requests.post(
                    url=target_url,
                    headers=headers,
                    data=request.body
                ),
                HttpMethod.DELETE: lambda request: requests.delete(
                    url=target_url,
                    headers=headers,
                    data=request.body
                ),
                HttpMethod.PUT: lambda request: requests.put(
                    url=target_url,
                    headers=headers,
                    data=request.body
                ),
                HttpMethod.HEAD: lambda request: requests.head(
                    url=target_url,
                    headers=headers
                )
            }

            method = HttpMethod.from_int(message.status_code)
            if method not in handlers:
                raise Exception('Unsupported HTTP method')

            response = handlers[method](message)
            response_message = ForwardingUdpControlListener \
                .create_message_response(
                    request=message,
                    response=response
                )

            result_status = response_message.status_code

            event.set_message_response(
                response=response_message
            )
        except Exception as e:
            print("An exception has occurred while processing request.",
                  file=sys.stderr)

            print(e, file=sys.stderr)
            traceback.print_exc()
            result_status = 500

            try:
                response = ForwardingUdpControlListener \
                    .create_error_response(
                        error_code=500
                    )

                event.set_message_response(
                    response=response
                )
            except Exception:
                print("A response could not be created for the error.",
                      file=sys.stderr)
                print(e, file=sys.stderr)
                traceback.print_exc()
        finally:
            time = datetime.strftime(
                datetime.now(),
                '%d-%b-%Y %H:%M:%S'
            )
            method = HttpMethod.from_int(
                event.message.status_code,
                raise_error=False
            )

            method = HttpMethod.to_string(method)

            print(f'{sender_ip} [{time}] UDP '
                  f'\"{method} {event.message.url}\" '
                  f'{result_status}')

    @staticmethod
    def get_headers(message: GenericMessage):
        """
        Gets the headers from a GenericMessage, as a dictionary
        :param message: The message to get the headers from
        :return: The headers, from the message, as a dictionary
        """
        try:
            headers = json.loads('{' + message.headers + '}')
        except JSONDecodeError:
            headers = {}

        if not isinstance(headers, dict):
            raise ValueError('Headers must be a dict.')

        ct_key = 'Content-Type'
        if ct_key not in headers:
            headers[ct_key] = 'application/json'

        for key, value in headers.items():
            if not isinstance(key, str):
                raise ValueError('Header keys must be strings.')

            if not isinstance(value, str):
                raise ValueError('Header values must be strings.')

        return headers
