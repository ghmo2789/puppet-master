from datetime import datetime

from control_server.src.controller import controller
from control_server.src.utils.time_utils import time_now


def seen_client(client_id: str) -> bool:
    """
    Mark a client as seen
    :param client_id: The id of the client
    :return: True if the client was marked as seen, False otherwise (i.e. if
    the client does not exist)
    """
    client = controller.db.get_client(
        client_id=client_id
    )

    if client is None:
        return False

    client.set_last_seen(time_now())
    controller.db.set_client(
        client_id=client_id,
        client=client,
        overwrite=True
    )

    return True
