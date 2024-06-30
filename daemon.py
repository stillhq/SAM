import asyncio
import pickle
from typing import List, Tuple
import sam.quick
from sam.actions import Action, Task
from sam.managers.utils import run_action, get_managers_dict

import dbus, dbus.service, dbus.mainloop.glib
import threading

try:
    import sadb
except ImportError:
    sadb = None


def sadb_update_installed():
    if sadb:
        try:
            sadb.update_installed()
        except Exception as e:
            pass # We don't care if this errors


class SamService(dbus.service.Object):
    queue: List[Action] = []
    available_updates: List[Action] = []

    def __init__(self):
        bus_name = dbus.service.BusName('io.stillhq.SamService', bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, '/io/stillhq/SamService')
        thread = threading.Thread(target=self.queue_manager)
        thread.daemon = True
        thread.start()

    def progress_trigger(self, progress: int):
        self.write_queue()
        self.progress_changed(progress)

    @dbus.service.signal('io.stillhq.SamService')
    def queue_changed(self):
        pass

    @dbus.service.signal('io.stillhq.SamService', signature="i")
    def progress_changed(self, progress: int):
        pass

    @dbus.service.signal('io.stillhq.SamService')
    def error_occurred(self, action):
        pass

    def add_to_queue(self, action: Action):
        # Check if action from package is already in the queue
        for existing_action in self.queue:
            if existing_action.package_id == action.package_id:
                return
        self.queue.append(action)
        self.write_queue()
        self.queue_changed()

    @dbus.service.method('io.stillhq.SamService', in_signature='a{sv}')
    def add_dict_to_queue(self, action_dict: dict):
        action = Action.from_dict(action_dict)
        for queue_action in self.queue:
            if queue_action.package_id == action.package_id:
                if action.task == Task.REMOVE and not queue_action.running:
                    self.queue.remove(queue_action)
                else:
                    return
        self.queue.append(action)
        self.write_queue()
        self.queue_changed()

    @dbus.service.method('io.stillhq.SamService')
    def remove_from_queue(self, package_name: str):
        for action in self.queue:
            if action.package_id == package_name:
                self.queue.remove(action)
        self.write_queue()
        self.queue_changed()

    @dbus.service.method('io.stillhq.SamService')
    def get_queue_actions_dict(self) -> List[dict]:
        if len(self.queue) == 0:
            return None
        return [action.to_dict() for action in self.queue]

    # @dbus.service.method('io.stillhq.SamService')
    # def get_updates_available(self) -> List[Tuple[str, str]]:
    #     updates = []
    #     for source, manager in get_managers_dict().items():
    #         for app in manager.check_updates():
    #             updates.append((source, app))
    #     if len(updates) is None:
    #         return None
    #     return updates

    # @dbus.service.method('io.stillhq.SamService')
    # def get_installed(self) -> List[Tuple[str, str]]:
    #     installed = []
    #     print(get_managers_dict().items())
    #     for source, manager in get_managers_dict().items():
    #         print(source, manager, manager.check_installed())
    #         for app in manager.check_installed():
    #             installed.append((source, app))
    #     if len(installed) == 0:
    #         return None  # Prevent dbus signature error from empty list
    #     return installed

    def write_queue(self):
        queue_dump = None
        if len(self.queue) > 0:
            queue_dump = [action.to_dict() for action in self.queue]
        with open(sam.quick.QUEUE_LOCATION, "wb") as file:
            pickle.dump(queue_dump, file)

    def queue_manager(self):
        print("Started Queue Manager")
        while True:
            if len(self.queue) > 0:
                action = self.queue[0]
                action.progress_trigger = self.progress_trigger
                run_action(action)
                if action.error and action.error != "":
                    print(action.error)
                    self.error_occurred(action.to_dict())
                sadb_update_installed()
                self.queue.pop(0)
                self.queue_changed()
                self.write_queue()

