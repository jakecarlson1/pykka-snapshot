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
            self.saved_channels[(n.id_short, snapshotable_actor.id_short)] = Channel()

    def is_in_progress(self):
        print({k:c.is_recording for k,c in self.saved_channels.items()})
        return sum([c.is_recording for c in self.saved_channels.values()]) > 0

    def save_message(self, message):
        self.saved_channels[message.get_channel()].add_message(message)

    def mark_channel_closed(self, channel):
        self.saved_channels[channel].is_recording = False

