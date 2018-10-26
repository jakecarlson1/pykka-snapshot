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
        self.attrs_of_super = {}
        self.attrs_to_save = {}
        self.attrs_of_super = set(self.__dict__.keys())

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
            snapshot_id = self._start_snapshot()
            self._send_mark_to_neighbors(snapshot_id)
            return True
        elif msg_obj["mark_snapshot"] != None:
            snapshot_id = msg_obj["mark_snapshot"]
            print("mark snapshot", snapshot_id)
            # TODO: see if snapshot in progress with id, if not, save state

        # TODO: see if snapshot in progress, if yes save msg for channel

        return False

    def _update_attrs_to_save(self):
        self.attrs_to_save = set(self.__dict__.keys()) - self.attrs_of_super

    def _start_snapshot(self):
        snapshot_id = uuid4()
        snapshot = Snapshot(snapshot_id)
        self._update_attrs_to_save()
        if len(self.attrs_to_save) == 0:
            print("No attributes given to save")
        snapshot.save_actor_state(self)
        self.snapshots[snapshot_id] = snapshot
        
        return snapshot_id

    def _send_mark_to_neighbors(self, snapshot_id):
        mark_msg_data = { "mark_snapshot" : snapshot_id }
        for n in self.neighbors:
            mark_msg = Message(self.id_short, n.id_short, mark_msg_data)
            n.ref.tell(mark_msg.as_sendable())

