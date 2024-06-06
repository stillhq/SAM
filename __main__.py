#!/usr/bin/env python3
import os

import sam.daemon
from gi.repository import GLib
import dbus.mainloop.glib

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("Please run SAM with root")
        exit(3)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    dbus_service = sam.daemon.SamService()

    loop = GLib.MainLoop()
    loop.run()
