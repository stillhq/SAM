from typing import List, Dict
from sam.managers import Manager
from sam.actions import Action

import threading

import gi.repository
gi.require_version('Flatpak', '1.0')
from gi.repository import Flatpak, GLib, Gio


class FlatpakManager(Manager):
    title: str
    manager_id: str
    current_action = Action
    flatpak_operation: Flatpak.TransactionOperation = None
    flatpak_progress: Flatpak.TransactionProgress = None

    @property
    def manager_type(self) -> str:  # Hardcoded property
        return "flatpak"

    def update_progress(self, progress):
        self.current_action.progress = progress.get_progress()
        print(self.current_action.progress)

    def new_operation(self, _transaction, operation, progress):
        self.flatpak_operation = operation
        self.flatpak_progress = progress
        self.flatpak_progress.connect("changed", self.update_progress)

    # Used for error handling
    def run_transaction(self, transaction):
        try:
            transaction.run(self.cancellable)
        except GLib.GError as error:
            self.current_action.error = error.message

    def on_error(self, _transaction, _operation, error, _error_details):
        self.current_action.error = error.message

    def create_transaction(self):
        transaction = Flatpak.Transaction.new_for_installation(self.flatpak_installation, self.cancellable)
        transaction.connect("new-operation", self.new_operation)
        transaction.connect("operation-error", self.on_error)
        return transaction

    def __init__(self, title: str, manager_id: str):
        super().__init__(title, manager_id)
        self.remote = title
        self.flatpak_installation = Flatpak.Installation.new_system()
        self.cancellable = Gio.Cancellable()

    def install(self, action: Action):
        transaction = self.create_transaction()
        transaction.add_install(self.manager_id, action.package_id, None)
        self.run_transaction(transaction)

    def remove(self, action: Action):
        transaction = self.create_transaction()
        transaction.add_uninstall(action.package_id)
        self.run_transaction(transaction)

    def update(self, action: Action):
        transaction = self.create_transaction()
        transaction.add_update(action.package_id)
        self.run_transaction(transaction)

    def check_update(self, package: str) -> bool:
        # Parsing the package name to get the RefKind
        ref = package.split("/")
        if ref[0] == "app":
            ref_kind = Flatpak.RefKind.APP
        else:
            ref_kind = Flatpak.RefKind.RUNTIME
        arch = ref[2]
        branch = ref[3]
        installed_ref = self.flatpak_installation.get_installed_ref(ref_kind, ref[1], arch, branch, self.cancellable)
        return installed_ref.get_is_current()

    def check_updates(self) -> List[str]:
        refs = self.flatpak_installation.list_installed_refs_for_update()
        return [package_from_ref(ref) for ref in refs]

    def check_installed(self) -> List[str]:
        refs = self.flatpak_installation.list_installed_refs()
        return [package_from_ref(ref) for ref in refs]


def get_managers_for_remotes() -> Dict[str, FlatpakManager]:
    installation = Flatpak.Installation.new_system()
    remotes = installation.list_remotes()
    managers = {}
    for remote in remotes:
        title = remote.get_title() if remote.get_title() else remote.get_name()
        managers[remote.get_name()] = FlatpakManager(title, remote.get_name())
    return managers


def package_from_ref(ref: Flatpak.Ref):
    kind = ""
    if ref.get_kind() == Flatpak.RefKind.APP:
        kind = "app"
    elif ref.get_kind() == Flatpak.RefKind.RUNTIME:
        kind = "runtime"

    return f"{kind}/{ref.get_name()}/{ref.get_arch()}/{ref.get_branch()}"
