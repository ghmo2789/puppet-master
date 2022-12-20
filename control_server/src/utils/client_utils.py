from control_server.src.controller import controller
from control_server.src.utils.time_utils import time_now


def seen_client(client_id: str, is_newly_started: bool = False) -> bool:
    """
    Mark a client as seen
    :param client_id: The id of the client
    :param is_newly_started: Whether the client is newly started, i.e. if the
    client was seen through a new init request
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

    # Update the client in the client tracker if there is a tracker
    if controller.client_tracker is not None:
        controller.client_tracker.mark_as_seen(
            client_id=client_id,
            polling_time=client.polling_time,
            is_newly_started=is_newly_started
        )

    return True
