from typing import List
from actions import Action

import dbus, dbus.service, dbus.mainloop.glib

from gi.repository import GLib


class SamService(dbus.service.Object):

    queue: List[Action] = []
    available_updates: List[Action] = []

    def __init__(self):
        bus_name = dbus.service.BusName('io.stillhq.SamService', bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, '/io/stillhq/SamService')

    @dbus.service.method('io.stillhq.SamService')
    def add_to_queue(self, action: Action):
        # Check if action from package is already in the queue
        for existing_action in self.queue:
            if existing_action.package_id == action.package_id:
                return
        self.queue.append(action)

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
    def get_queue_packages(self) -> List[str]:
        return [action.package_id for action in self.queue]

    def queue_manager(self):
        while True:
            if len(self.queue) > 0:
                pass


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    dbus_service = SamService()

    loop = GLib.MainLoop()
    loop.run()