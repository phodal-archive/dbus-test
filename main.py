#!/usr/bin/python

import gi

from account import MyBuddyCallback, MyAccountCallback

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import pjsua as pj

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gobject

LOG_LEVEL = 3
pending_pres = None
pending_uri = None


def log_cb(level, str, len):
    print str,


class DialogExample(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label("This is a dialog to display additional information")

        box = self.get_content_area()
        box.add(label)
        self.show_all()


class MyWindow(Gtk.Window):
    def __init__(self):
        self.draw_ui()
        self.init_pjsua()
        self.bus = dbus.SessionBus()

    def init_pjsua(self):
        lib = pj.Lib()
        try:
            # Init library with default config and some customized
            # logging config.
            lib.init(log_cfg=pj.LogConfig(level=LOG_LEVEL, callback=log_cb))

            # Create UDP transport which listens to any available port
            transport = lib.create_transport(pj.TransportType.UDP,
                                             pj.TransportConfig(0))
            print "\nListening on", transport.info().host,
            print "port", transport.info().port, "\n"

            # Start the library
            lib.start()

            # Create local account
            self.acc = lib.create_account_for_transport(transport, cb=MyAccountCallback())
            self.acc.set_basic_status(True)

            self.my_sip_uri = "sip:" + transport.info().host + \
                              ":" + str(transport.info().port)

            self.sip_address_label.set_label(self.my_sip_uri)
            self.buddy = None

        except pj.Error, e:
            print "Exception: " + str(e)
            lib.destroy()
            lib = None

    def draw_ui(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.set_size_request(200, 100)
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        self.sip_address_label = Gtk.Button()
        self.sip_address_label.set_label("SIP Address")
        self.sip_address_label.connect("clicked", self.copy_text)
        self.clipboard.set_text(self.sip_address_label.get_label(), -1)
        vbox.pack_start(self.sip_address_label, True, True, 0)
        self.sip_text = Gtk.Entry()
        self.sip_text.set_text('sip')
        vbox.pack_start(self.sip_text, True, True, 0)
        hbox = Gtk.Box(spacing=6)
        vbox.pack_start(hbox, True, True, 0)
        self.connect_button = Gtk.Button(label="connect")
        self.connect_button.connect("clicked", self.connect_server)
        hbox.pack_start(self.connect_button, True, True, 0)
        self.msg_text = Gtk.Entry()
        self.msg_text.set_text('message')
        vbox.pack_start(self.msg_text, True, True, 0)
        self.send_message_button = Gtk.Button(label="send")
        self.send_message_button.connect("clicked", self.send_message)
        vbox.pack_start(self.send_message_button, True, True, 0)

    def copy_text(self, widget):
        self.clipboard.set_text(self.sip_address_label.get_label(), -1)

    def connect_server(self, widget):
        self.buddy = self.acc.add_buddy(self.my_sip_uri, cb=MyBuddyCallback())

        service = self.bus.get_object('com.example.service', "/com/example/service")
        self._message = service.get_dbus_method('get_message', 'com.example.service.Message')

        self.buddy.subscribe()

    def send_message(self, widget):
        print("Send Message")


class MyDBUSService(dbus.service.Object):
    def __init__(self, message):
        self._message = message

    def run(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName("com.example.service", dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/com/example/service")

        self._loop = gobject.MainLoop()
        print "Service running..."
        self._loop.run()
        print "Service stopped"

    @dbus.service.method("com.example.service.Message", in_signature='', out_signature='s')
    def get_message(self):
        print "  sending message"
        return self._message

    @dbus.service.method("com.example.service.Quit", in_signature='', out_signature='')
    def quit(self):
        print "  shutting down"
        self._loop.quit()


win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()

MyDBUSService("hello")
Gtk.main()
