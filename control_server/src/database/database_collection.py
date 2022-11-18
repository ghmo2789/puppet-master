from enum import StrEnum


class DatabaseCollection(StrEnum):
    """Database collections"""
    USERS = "users"
    USER_TASKS = "user_tasks"
    USER_TASK_RESPONSES = "user_task_responses"

    def get_name(self):
        return self.value
