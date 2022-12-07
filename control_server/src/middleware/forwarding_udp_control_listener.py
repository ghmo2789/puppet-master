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
    method_handlers: dict[
        HttpMethod,
        Callable[[GenericMessage, str, dict[str, str]], requests.Response],
    ] = {
        HttpMethod.GET: lambda request, url, headers: requests.get(
            url=url,
            headers=headers
        ),
        HttpMethod.POST: lambda request, url, headers: requests.post(
            url=url,
            headers=headers,
            data=request.body
        ),
        HttpMethod.DELETE: lambda request, url, headers: requests.delete(
            url=url,
            headers=headers,
            data=request.body
        ),
        HttpMethod.PUT: lambda request, url, headers: requests.put(
            url=url,
            headers=headers,
            data=request.body
        ),
        HttpMethod.HEAD: lambda request, url, headers: requests.head(
            url=url,
            headers=headers
        )
    }

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

            response_message = self._get_message_response(
                message=event.message,
                sender_ip=sender_ip
            )

            result_status = response_message.status_code

            event.set_message_response(
                response=response_message
            )
        except Exception as e:
            ForwardingUdpControlListener.log_error(
                e,
                "An exception has occurred while processing a UDP request."
            )
            result_status = 500

            try:
                response = ForwardingUdpControlListener \
                    .create_error_response(
                        error_code=500
                    )

                event.set_message_response(
                    response=response
                )
            except Exception as e2:
                ForwardingUdpControlListener.log_error(
                    e2,
                    "A response could not be created for the error."
                )
        finally:
            ForwardingUdpControlListener.log_request(
                sender_ip=sender_ip,
                status_code=event.message.status_code,
                url=event.message.url,
                result_status=result_status
            )

    def _get_message_response(self, message: GenericMessage, sender_ip: str):
        target_url = self.api_base_url + message.url
        headers = ForwardingUdpControlListener.get_headers(message)

        ForwardingUdpControlListener._append_forward_header_ip(
            headers=headers,
            ip=sender_ip
        )

        method = HttpMethod.from_int(message.status_code)
        if method not in ForwardingUdpControlListener.method_handlers:
            raise Exception('Unsupported HTTP method')

        handler = ForwardingUdpControlListener.method_handlers[method]
        response = handler(message, target_url, headers)
        return ForwardingUdpControlListener \
            .create_message_response(
                request=message,
                response=response
            )

    @staticmethod
    def _append_forward_header_ip(headers: dict[str, str], ip: str):
        """
        Appends the given IP to the X-Forwarded-For header
        :param headers: The headers to append to
        :param ip: The IP to append
        :return: Nothing
        """
        forward_header_name = 'X-Forwarded-For'
        if forward_header_name in headers:
            headers[forward_header_name] += ', ' + ip
        else:
            headers[forward_header_name] = ip

    @staticmethod
    def log_error(exception: Exception, message: str = None):
        if message is not None:
            print(message, file=sys.stderr)

        print(exception, file=sys.stderr)
        traceback.print_exc()

    @staticmethod
    def log_request(
            sender_ip: str,
            status_code: int,
            url: str,
            result_status: int):
        """
        Logs a request to stdout
        :param sender_ip: The requests senders IP
        :param status_code: The status code contained in the request
        :param url: The requested URL
        :param result_status: The resulting status code of the request
        :return: None
        """
        time = datetime.strftime(
            datetime.now(),
            '%d-%b-%Y %H:%M:%S'
        )
        method = HttpMethod.from_int(
            status_code,
            raise_error=False
        )

        method = HttpMethod.to_string(method)

        print(f'{sender_ip} [{time}] UDP '
              f'\"{method} {url}\" '
              f'{result_status}')

    @staticmethod
    def get_headers(message: GenericMessage) -> dict[str, str]:
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
