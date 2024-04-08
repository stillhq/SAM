import daemon

from gi.repository import GLib
import dbus.mainloop.glib

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    dbus_service = daemon.SamService()

    loop = GLib.MainLoop()
    loop.run()
