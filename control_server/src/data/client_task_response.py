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
            result: str = None,
            status: int = None):
        super().__init__(result=result, status=status)
        self.id: str = task_id
