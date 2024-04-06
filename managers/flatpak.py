from typing import List
from . import Manager

import actions
import threading

import gi.repository
gi.require_version('Flatpak', '1.0')
from gi.repository import Flatpak, Gio


def package_from_ref(ref: Flatpak.Ref):
    kind = ""
    if ref.get_kind() == Flatpak.RefKind.APP:
        kind = "app"
    elif ref.get_kind() == Flatpak.RefKind.RUNTIME:
        kind = "runtime"

    return f"{kind}/{ref.get_name()}/{ref.get_arch()}/{ref.get_branch()}"


class FlatpakManager(Manager):
    title: str
    manager_id: str
    action = actions.Action
    flatpak_operation: Flatpak.TransactionOperation = None
    flatpak_progress: Flatpak.Progress = None

    @property
    def manager_type(self) -> str:  # Hardcoded property
        return "flatpak"

    def update_progress(self):
        if self.flatpak_progress is not None:
            self.action.progress = self.flatpak_progress.get_progress()

    def new_operation(self, _transaction, operation, progress):
        self.flatpak_operation = operation
        self.flatpak_progress = progress
        thread = threading.Thread(target=self.update_progress)
        thread.daemon = True
        thread.start()

    def on_error(self, _transaction, _operation, error, _error_details):
        self.action.error = error.message

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

    def install(self, package: str):
        self.transaction = self.create_transaction()
        self.transaction.add_install(self.title, package, None)
        self.transaction.run(self.cancellable)

    def remove(self, package: str):
        self.transaction = self.create_transaction()
        self.transaction.add_uninstall(package)
        self.transaction.run(self.cancellable)

    def update(self, package: str):
        self.transaction = self.create_transaction()
        self.transaction.add_update(package)
        self.transaction.run(self.cancellable)

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