from enum import Enum
import flatpak


class ManagerID(Enum):
    OSTREE = 0
    FLATPAK = 1