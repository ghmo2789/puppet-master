from typing import List, Iterable
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network, \
    ip_address, ip_network

from flask import Request
from control_server.src.controller import controller

trusted_proxies: set[IPv4Network | IPv6Network] | None = None


def _get_addr(addr: str, network=True) -> \
    IPv4Network | IPv6Network | IPv4Address | IPv6Address:
    """
    Gets the address from the given string
    :param addr: The address to get
    :return: The address
    """
    if network:
        return ip_network(addr)
    else:
        return ip_address(addr)


def to_ip_list(ips: List[str], network=True) -> \
        List[IPv4Network | IPv6Network | IPv4Address | IPv6Address]:
    return [_get_addr(addr, network=network) for addr in ips]

def get_trusted_proxies() -> set[IPv4Network | IPv6Network]:
    """
    Gets the trusted proxies
    :return: The trusted proxies
    """
    return set(to_ip_list(
        controller.settings.trusted_proxies_set,
        network=True
    ))

def contains_ip(
        ip: IPv4Address | IPv6Address,
        ip_list: Iterable[IPv4Network | IPv6Network]):
    for listed_ip in ip_list:
        if ip in listed_ip:
            return True

    return False


def get_ip(request: Request) -> str:
    """
    Gets the IP address of the client from the request
    :param request: The request to get the IP address from
    :return: The IP address of the client
    """
    global trusted_proxies
    if trusted_proxies is None:
        trusted_proxies = get_trusted_proxies()

    route = reversed(to_ip_list(
        request.access_route + [request.remote_addr],
        network=False
    ))

    for addr in route:
        if not contains_ip(addr, trusted_proxies):
            return str(addr)

    return str(request.remote_addr)
