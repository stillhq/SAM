from enum import Enum
from typing import Type, Callable


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
    app_name: str
    manager_id: str
    running: bool = False
    task: Task
    _progress: int = 0
    progress_trigger: Callable = None
    error: str = ""
    status: str = ""
    background: bool = False

    @property
    def progress(self) -> int:
        return self._progress

    @progress.setter
    def progress(self, value: int):
        self._progress = value
        if self.progress_trigger is not None:
            self.progress_trigger(value)

    def notification_message(self) -> str:
        match self.task:
            case Task.INSTALL:
                return f"Installing {self.app_name}"
            case Task.REMOVE:
                return f"Removing {self.app_name}"
            case Task.UPDATE:
                return f"Updating {self.app_name}"
            case Task.UNKNOWN:
                return f"Unknown task for {self.app_name}"

    def to_dict(self) -> dict:  # NEEDED FOR DBUS
        return {
            "package_id": self.package_id,
            "app_name": self.app_name,
            "manager_id": self.manager_id,
            "task": self.task.to_str(),
            "progress": str(self.progress),
            "error": self.error,
            "background": str(self.background),
            "status": str(self.background)
        }

    @classmethod
    def from_dict(cls, data: dict):
        action = cls()
        action.package_id = str(data["package_id"])
        action.app_name = str(data["app_name"])
        action.manager_id = str(data["manager_id"])
        action.task = Task.from_str(str(data["task"]))
        action.background = bool(data.get("background", False))
        action.progress = int(data.get("progress", "0"))

        return action


