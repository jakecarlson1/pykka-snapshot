from datetime import datetime
from pykka import ThreadingActor
from pykka.registry import ActorRegistry
from snapshotting import Message, Neighbor, Snapshot
from uuid import uuid4
import inspect
import json
import os
import pickle

class SnapshotableActor(ThreadingActor):
    def __init__(self):
        super().__init__()
        self.id = self.actor_urn
        self.id_short = self.shorten_id()
        # TODO: dynamically record neighbors
        self.neighbors = []
        self.snapshots = {}
        with open(os.path.dirname(os.path.abspath(__file__)) + "/config/snapshotdir.txt", "r") as f:
            self.snapshot_dir = f.read().strip()
        self.attrs_to_save = {}
        self.attrs_of_super = {}
        self.attrs_of_super = set(self.__dict__.keys())

    def save_neighbors(self, instances, proxies=True):
        if proxies:
            self.neighbors = [Neighbor().from_proxy(p) for p in instances]
        else:
            self.neighbors = [Neighbor().from_actor(a) for a in instances]

    def send_message_to_neighbor(self, i, msg_data):
        receiver = self.neighbors[i]
        msg = Message(self.id_short, receiver.id_short, msg_data)
        self.neighbors[i].ref.tell(msg.as_sendable())

    def send_message_to_self(self, msg_data):
        msg = Message(self.id_short, self.id_short, msg_data)
        self.actor_ref.tell(msg.as_sendable())

    def shorten_id(self):
        return self.id.split(":")[2].split("-")[0]

    def on_receive(self, message):
        msg_obj = message['obj']
        if msg_obj["init_snapshot"] == True:
            print("start snapshot")
            snapshot_id = self._take_snapshot()
            snapshot_path = self._make_snapshot_directory(snapshot_id)

            return True

        elif msg_obj["mark_snapshot"] != None:
            snapshot_id = msg_obj["mark_snapshot"]
            print("mark snapshot", snapshot_id)
            if snapshot_id not in self.snapshots.keys():
                self._take_snapshot(snapshot_id)
                self.snapshots[snapshot_id].mark_channel_closed(msg_obj.get_channel())
            else:
                self.snapshots[snapshot_id].mark_channel_closed(msg_obj.get_channel())
            if not self.snapshots[snapshot_id].is_in_progress():
                self._post_process_snapshot(snapshot_id)

            return True

        else:
            in_progress = [s for s in self.snapshots.values() if s.is_in_progress()]
            channel = msg_obj.get_channel()
            if len(in_progress) > 0 and channel[0] != channel[1]:
                for s in in_progress:
                    s.save_message(msg_obj)

        return False

    def _update_attrs_to_save(self):
        self.attrs_to_save = set(self.__dict__.keys()) - self.attrs_of_super

    def _take_snapshot(self, snapshot_id=None):
        if snapshot_id == None:
            snapshot_id = uuid4()
        snapshot = Snapshot(snapshot_id)
        self._update_attrs_to_save()
        if len(self.attrs_to_save) == 0:
            print("No attributes to save")
        snapshot.save_actor_state(self)
        self.snapshots[snapshot_id] = snapshot
        self._send_mark_to_neighbors(snapshot_id)

        return snapshot_id

    def _send_mark_to_neighbors(self, snapshot_id):
        mark_msg_data = { "mark_snapshot" : snapshot_id }
        for n in self.neighbors:
            mark_msg = Message(self.id_short, n.id_short, mark_msg_data)
            n.ref.tell(mark_msg.as_sendable())

    def _post_process_snapshot(self, snapshot_id):
        print("save snapshot", snapshot_id)
        class_name = self.__class__.__name__
        snapshot_path = self.snapshot_dir + "/" + str(snapshot_id)
        file_name = "{}/{}-{}.pkl".format(snapshot_path, class_name, self.id_short)
        with open(file_name, "wb") as f:
            pickle.dump(self.snapshots[snapshot_id], f)
        with open(snapshot_path + "/info.txt", "a") as f:
            f.write("{}-{}: {}\n".format(
                class_name, self.id_short, self._json_save_dict()
            ))

    def _make_snapshot_directory(self, snapshot_id):
        snapshot_path = self.snapshot_dir + "/" + str(snapshot_id)
        if not os.path.exists(snapshot_path):
            os.mkdir(snapshot_path)
            with open(snapshot_path + "/info.txt", "w") as f:
                f.write("START: {}\n".format(datetime.now()))

        return snapshot_path

    def _json_save_dict(self):
        class_path = inspect.getfile(self.__class__)
        data = {
            'class_path': class_path,
            'timestamp': str(datetime.now())
        }

        return json.dumps(data, indent=4)

    def _register(self):
        ActorRegistry.register(self.actor_ref)

    def _restart(self):
        self._start_actor_loop()
        return self.actor_ref

