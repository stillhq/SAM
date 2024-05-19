from typing import List, Tuple
from sam.actions import Action
from sam.managers.utils import run_action, get_managers_dict

import dbus, dbus.service, dbus.mainloop.glib

import threading


class SamService(dbus.service.Object):
    queue: List[Action] = []
    available_updates: List[Action] = []
    notify_service = dbus.Interface(
        dbus.SessionBus().get_object(
            "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
        ), "org.freedesktop.Notifications"
    )
    notify_id = 0
    queue_pos = 0
    queue_length: int = 0

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
        self.queue_length += 1

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

    @dbus.service.method('io.stillhq.SamService')
    def get_updates_available(self) -> List[Tuple[str, str]]:
        updates = []
        for source, manager in get_managers_dict().items():
            for app in manager.check_updates():
                updates.append((source, app))
        if len(updates) is None:
            return None
        return updates

    @dbus.service.method('io.stillhq.SamService')
    def get_installed(self) -> List[Tuple[str, str]]:
        installed = []
        print(get_managers_dict().items())
        for source, manager in get_managers_dict().items():
            print(source, manager, manager.check_installed())
            for app in manager.check_installed():
                installed.append((source, app))
        if len(installed) is None:
            return None
        return installed

    @dbus.service.method('io.stillhq.SamService')
    def bare_app_info(self, source: str, package: str) -> dict:
        print("hell")
        return get_managers_dict()[source].bare_app_info(package)

    def queue_manager(self):
        print("Started Queue Manager")
        while True:
            if len(self.queue) > 0:
                action = self.queue[0]

                urgency = 0
                if not action.background:
                    urgency = 1

                self.queue_pos += 1

                self.notify_id = self.notify_service.Notify(
                    "still App Manager", self.notify_id, "system-software-install-symbolic",
                    action.notification_message() + f" {self.queue_pos}/{self.queue_length}", [],
                    {
                        "urgency": urgency,
                        "desktop-entry": "io.stillhq.SamService.desktop",
                        "category": "transfer",
                        "transient": False
                    }, -1
                )
                run_action(action)
                self.queue.pop(0)
            else:
                self.queue_pos = 0
                self.queue_length = 0
                self.notify_service.CloseNotification(self.notify_id)
                self.notify_id = 0
