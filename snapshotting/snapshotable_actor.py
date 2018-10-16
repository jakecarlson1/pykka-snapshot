from pykka import ThreadingActor
from snapshotting import message

class SnapshotableActor(ThreadingActor):
    def __init__(self):
        super().__init__()
        self.id = self.actor_urn
        self.neighbor_proxies = []
        self.neighbor_ids = []

    def save_neighbors(self, proxies):
        self.neighbor_ids = [p.id.get() for p in proxies]
        self.neighbor_proxies = proxies

        loc = self.neighbor_ids.index(self.id)
        del self.neighbor_ids[loc]
        del self.neighbor_proxies[loc]

    def send_message_to_neighbor(self, i, msg_data):
        receiver_id = self.neighbor_ids[i]
        msg = Message(self.id, receiver_id, msg_data)
        self.neighbor_proxies[i].tell(msg)

    def send_message_to_self(self, msg_data):
        msg = Message(self.id, self.id, msg_data)
        self.actor_ref.tell(msg)

    # TODO: overload on receive to handle snapshot messages
