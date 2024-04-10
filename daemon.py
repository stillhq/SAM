from typing import List
from actions import Action
from managers.utils import run_action

import dbus, dbus.service, dbus.mainloop.glib

import threading

class SamService(dbus.service.Object):

    queue: List[Action] = []
    available_updates: List[Action] = []

    def __init__(self):
        bus_name = dbus.service.BusName('io.stillhq.SamService', bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, '/io/stillhq/SamService')

        thread = threading.Thread(target=self.queue_manager)
        thread.daemon = True
        thread.start()

    def add_to_queue(self, action: Action):
        # Check if action from package is already in the queue
        for existing_action in self.queue:
            if existing_action.package_id == action.package_id:
                return
        self.queue.append(action)

    @dbus.service.method('io.stillhq.SamService')
    def add_dict_to_queue(self, action_dict: dict):
        for action in self.queue:
            if action.package_id == action_dict["package_id"]:
                return
        self.queue.append(Action.from_dict(action_dict))

    @dbus.service.method('io.stillhq.SamService')
    def remove_from_queue(self, package_name: str):
        for action in self.queue:
            if action.package_id == package_name:
                self.queue.remove(action)

    @dbus.service.method('io.stillhq.SamService')
    def get_queue_actions_dict(self) -> List[dict]:
        return [action.to_dict() for action in self.queue]

    def queue_manager(self):
        print("Started Queue Manager")
        while True:
            if len(self.queue) > 0:
                action = self.queue[0]
                run_action(action)
                self.queue.pop(0)