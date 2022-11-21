from control_server.src.data.anonymous_client_task_response import \
    AnonymousClientTaskResponse


class ClientTaskResponse(AnonymousClientTaskResponse):
    def __init__(
            self,
            task_id: str = None,
            result: str = None,
            status: int = None):
        super().__init__(result=result, status=status)
        self.task_id: str = task_id
