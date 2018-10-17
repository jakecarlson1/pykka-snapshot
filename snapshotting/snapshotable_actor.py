from pykka import ThreadingActor
from snapshotting.message import Message
from snapshotting.neighbor import Neighbor

class SnapshotableActor(ThreadingActor):
    def __init__(self):
        super().__init__()
        self.id = self.actor_urn
        self.id_short = self.shorten_id()
        self.neighbors = []

    def save_neighbors(self, proxies):
        self.neighbors = [Neighbor(p) for p in proxies]

    def send_message_to_neighbor(self, i, msg_data):
        receiver = self.neighbors[i]
        msg = Message(self.id_short, receiver.id_short, msg_data)
        self.neighbors[i].ref.tell(msg.as_sendable())

    def send_message_to_self(self, msg_data):
        msg = Message(self.id_short, self.id_short, msg_data)
        self.actor_ref.tell(msg.as_sendable())

    def shorten_id(self):
        return self.id.split(":")[2].split("-")[0]

    # TODO: overload on receive to handle snapshot messages

