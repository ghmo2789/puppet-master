from typing import Dict

from control_server.src.data.anonymous_client_task_response import \
    AnonymousClientTaskResponse


class ClientTaskResponse(AnonymousClientTaskResponse):
    """
    Client response data class, featuring the response itself as well as the ID
    of the task being responded to.
    """
    def __init__(
            self,
            task_id: str = None,
            client_id: str = None,
            result: str = None,
            status: int = None):
        super().__init__(result=result, status=status)
        self._id: Dict[str, str] = {}

        if task_id is not None and client_id is not None:
            self.set_id(task_id, client_id)

    def set_id(self, task_id: str, client_id: str):
        if task_id is None or client_id is None:
            raise ValueError('Task ID and client ID must be set')

        self._id = {
            'client_id': client_id,
            'task_id': task_id
        }
