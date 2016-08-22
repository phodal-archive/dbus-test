import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pjsua as pj

LOG_LEVEL = 3
pending_pres = None
pending_uri = None

def log_cb(level, str, len):
    print str,

class MyAccountCallback(pj.AccountCallback):
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    def on_incoming_subscribe(self, buddy, from_uri, contact_uri, pres):
        global pending_pres, pending_uri
        # Allow buddy to subscribe to our presence
        if buddy:
            return (200, None)
        print 'Incoming SUBSCRIBE request from', from_uri
        print 'Press "A" to accept and add, "R" to reject the request'
        pending_pres = pres
        pending_uri = from_uri
        return (202, None)


class MyBuddyCallback(pj.BuddyCallback):
    def __init__(self, buddy=None):
        pj.BuddyCallback.__init__(self, buddy)

    def on_state(self):
        print "Buddy", self.buddy.info().uri, "is",
        print self.buddy.info().online_text

    def on_pager(self, mime_type, body):
        print "Instant message from", self.buddy.info().uri,
        print "(", mime_type, "):"
        print body

    def on_pager_status(self, body, im_id, code, reason):
        if code >= 300:
            print "Message delivery failed for message",
            print body, "to", self.buddy.info().uri, ":", reason

    def on_typing(self, is_typing):
        if is_typing:
            print self.buddy.info().uri, "is typing"
        else:
            print self.buddy.info().uri, "stops typing"

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.set_size_request(200, 100)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        sip_address_label = Gtk.Label()
        sip_address_label.set_text("SIP Address")
        sip_address_label.set_justify(Gtk.Justification.LEFT)
        vbox.pack_start(sip_address_label, True, True, 0)

        self.sip_text = Gtk.Entry()
        self.sip_text.set_text('sip')
        vbox.pack_start(self.sip_text, True, True, 0)

        hbox = Gtk.Box(spacing=6)
        vbox.pack_start(hbox, True, True, 0)

        self.button = Gtk.Button(label="connect")
        self.button.connect("clicked", self.connect_server)
        hbox.pack_start(self.button, True, True, 0)

        self.msg_text = Gtk.Entry()
        self.msg_text.set_text('message')
        vbox.pack_start(self.msg_text, True, True, 0)

        self.button = Gtk.Button(label="send")
        self.button.connect("clicked", self.send_message)
        vbox.pack_start(self.button, True, True, 0)

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

            my_sip_uri = "sip:" + transport.info().host + \
                         ":" + str(transport.info().port)

            sip_address_label.set_text(my_sip_uri)
            self.buddy = None

        except pj.Error, e:
            print "Exception: " + str(e)
            lib.destroy()
            lib = None

    def connect_server(self, widget):
        self.buddy = self.acc.add_buddy(input, cb=MyBuddyCallback())
        self.buddy.subscribe()

    def send_message(self, widget):
        print("Send Message")

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
