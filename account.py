import pjsua as pj
import dbus


class MyAccountCallback(pj.AccountCallback):
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)
        self.bus = dbus.SessionBus()

    def on_incoming_subscribe(self, buddy, from_uri, contact_uri, pres):
        if buddy:
            return (200, None)
        print 'Incoming SUBSCRIBE request from', from_uri
        pending_pres = pres
        pending_uri = from_uri

        service = self.bus.get_object('com.example.service', "/com/example/service")
        self._request = service.get_dbus_method('get_message', 'com.example.service.Message')
        self._request(str(from_uri), pending_pres, str(pending_uri))

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
