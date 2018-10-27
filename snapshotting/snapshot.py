from snapshotting import Channel

class Snapshot(object):
    def __init__(self, snapshot_id):
        self.id = snapshot_id
        self.saved_actor_state = {}
        self.saved_channels = {}

    def save_actor_state(self, snapshotable_actor):
        for k in snapshotable_actor.attrs_to_save:
            self.saved_actor_state[k] = snapshotable_actor.__dict__[k]
        for n in snapshotable_actor.neighbors:
            self.saved_channels[n.id] = Channel()

