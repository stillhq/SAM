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
    import sadb.database as db
except ImportError:
    sadb = None


def sadb_update_installed():
    if sadb:
        try:
            sadb.update_installed()
        except Exception as e:
            pass # We don't care if this errors


def get_app_name_from_sadb(package_name, package_source):
    if sadb:
        database = db.get_readable_db()
        app = database.get_installed_app(package_name, package_source)
        if app == None:
            print(f"Could not find {package_name}, {package_source} in sadb")
            return package_name
        if app.name:
            return app.name

    return package_name


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

    @dbus.service.method('io.stillhq.SamService', in_signature='b')
    def update_all(self, background):
        managers = get_managers_dict()
        for manager in get_managers_dict():
            for package in managers[manager].check_updates():
                action = Action()
                action.package_id = str(package)
                action.app_name = get_app_name_from_sadb(package, manager)
                action.manager_id = manager
                action.task = Task.UPDATE
                action.background = background
                self.add_to_queue(action)

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

