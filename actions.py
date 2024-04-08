from enum import Enum
from typing import Type


class Task(Enum):
    INSTALL = 0
    REMOVE = 1
    UPDATE = 2
    UNKNOWN = 100

    @classmethod
    def from_str(cls, s: str):
        return cls[s.upper()]

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
    def from_dict(cls, data: dict):
        action = cls()
        action.package_id = str(data["package_id"])
        action.manager_id = str(data["manager_id"])
        action.task = Task.from_str(str(data["task"]))
        return action

