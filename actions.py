from enum import Enum
from typing import Type


class Task(Enum):
    INSTALL = 0
    REMOVE = 1
    UPDATE = 2
    UNKNOWN = 100

    @staticmethod
    def from_str(s: str):
        return Task[s.upper()]

    def to_str(self) -> str:
        return self.name


class Action:
    package_id: str
    manager_id: str
    running: bool = False
    task: Task
    progress: int
    error: str = ""

    def to_dict(self) -> dict:  # NEEDED FOR DBUS
        return {
            "package_id": self.package_id,
            "manager_id": self.manager_id,
            "task": self.task.to_str(),
            "progress": self.progress,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: dict) -> Type['Action']:
        action = Action()
        action.package_id = data["package_id"]
        action.manager_id = data["manager_id"]
        action.task = data["task"]
        action.progress = data["progress"]
        action.error = data["error"]
        return cls

    def run_action(self):
        pass
        # TODO: Write this function after Managers are finished
