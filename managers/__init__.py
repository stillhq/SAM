from abc import ABC, abstractmethod
from typing import List

from sam.actions import Action


class Manager(ABC):
    title: str
    manager_id: str
    current_action = Action

    def __init__(self, title: str, manager_id: str):
        self.title = title
        self.manager_id = manager_id

    @property
    @abstractmethod
    def manager_type(self) -> str:  # Hardcoded property
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def install(self, action: Action):
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def remove(self, action: Action):
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def update(self, action: Action):
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def check_update(self, package: str) -> bool:
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def check_updates(self) -> List[str]:
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def check_installed(self) -> List[str]:
        raise NotImplementedError("Not implemented for manager type")
