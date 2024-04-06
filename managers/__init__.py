from abc import ABC, abstractmethod
from typing import List

import actions


class Manager(ABC):
    title: str
    manager_id: str
    action = actions.Action

    def __init__(self, title: str, manager_id: str):
        self.title = title
        self.manager_id = manager_id

    @property
    @abstractmethod
    def manager_type(self) -> str:  # Hardcoded property
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def install(self, package: str):
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def remove(self, package: str):
        raise NotImplementedError("Not implemented for manager type")

    @abstractmethod
    def update(self, package: str):
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