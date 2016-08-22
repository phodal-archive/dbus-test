import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# dbus imports
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop


# Main window class
class Window(dbus.service.Object):
    def __init__(self, gladeFilePath, name):
        # ... inicialization
        self.name = name
        self.busName = dbus.service.BusName('com.example.MyInterface', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, self.busName, '/com/example/MyInterface/' + self.name)

    @dbus.service.method('com.example.MyInterface.Window')
    def show(self):
        self.window.show_all()

    @dbus.service.method('com.example.MyInterface.Window')
    def destroy(self):
        Gtk.main_quit()

    @dbus.service.method('com.example.MyInterface.Window')
    def update(self, data):
        # top class 'update' method
        pass


# Child window class
class WindowOne(Window):
    def __init__(self, gladeFilePath):
        Window.__init__(self, gladeFilePath, "WindowOne")

    @dbus.service.method('com.example.MyInterface.WindowOne')
    def update(self, data):
        # reimplementation of top class 'update' method
        pass


if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)

    gladeFilePath = "/etc/interface.glade"
    windowOne = WindowOne(gladeFilePath)

    Gtk.main()
