import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.set_size_request(200, 100)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.entry = Gtk.Entry()
        self.entry.set_text('Hello World')
        vbox.pack_start(self.entry, True, True, 0)

        hbox = Gtk.Box(spacing=6)
        vbox.pack_start(hbox, True, True, 0)

        self.button = Gtk.Button(label="connect")
        self.button.connect("clicked", self.connect_server)
        hbox.pack_start(self.button, True, True, 0)

        self.button = Gtk.Button(label="message")
        self.button.connect("clicked", self.send_message)
        hbox.pack_start(self.button, True, True, 0)

    def connect_server(self, widget):
        print("Hello World")

    def send_message(self, widget):
        print("Send Message")


win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
