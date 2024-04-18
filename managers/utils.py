from typing import Dict
import sam.managers.flatpak as flatpak
from sam.managers import Manager
from sam.actions import Action, Task


def get_managers_dict() -> Dict[str, Manager]:
    managers = {}
    managers.update(flatpak.get_managers_for_remotes())
    return managers


def run_action(action: Action):
    manager = get_managers_dict()[action.manager_id]
    action.running = True
    try:
        match action.task:
            case Task.INSTALL:
                manager.install(action)
            case Task.REMOVE:
                manager.remove(action)
            case Task.UPDATE:
                manager.update(action)
    except Exception as e:  #
        action.error = str(e)

    action.running = False
