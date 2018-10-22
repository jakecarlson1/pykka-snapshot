from pykka import ThreadingActor
from snapshotting import Message, Neighbor, Snapshot
from uuid import uuid4

class SnapshotableActor(ThreadingActor):
    def __init__(self):
        super().__init__()
        self.id = self.actor_urn
        self.id_short = self.shorten_id()
        self.neighbors = []
        self.snapshots = {}
        self.attrs_to_save = []

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
    def on_receive(self, message):
        msg_obj = message['obj']
        if msg_obj["init_snapshot"] == True:
            print("start snapshot")
            self._start_snapshot()
            return True

        return False

    def _start_snapshot(self):
        snapshot_id = uuid4()
        snapshot = Snapshot(snapshot_id)
        if len(self.attrs_to_save) == 0:
            print("No attributes given to save")
        snapshot.save_actor_state(self)
        self.snapshots[snapshot_id] = snapshot

