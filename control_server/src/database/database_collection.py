from enum import StrEnum


class DatabaseCollection(StrEnum):
    """Database collections"""
    USERS = "users"
    USER_TASKS = "user_tasks"

    def get_name(self):
        return self.value
