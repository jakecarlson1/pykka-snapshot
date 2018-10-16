import numpy as np
from snapshotting.snapshotable_actor import SnapshotableActor

class Incrementor(SnapshotableActor):
    def __init__(self, msg_send_prob):
        super().__init__()
        self.logical_clock = 0
        self.msg_send_prop = msg_send_prob

    def on_receive(self, message):
        super().on_receive(message)

        self.logical_clock = max(message["logical_clock"], self.logical_clock) + 1

        self._can_send_message_to_neighbor()

        self._send_message_to_self()

    def _can_send_message_to_neighbor():
        val = np.random.random_sample()
        if val >= self.msg_send_prop:
            self.logical_clock += 1

            idx = np.random.randint(0, len(self.neighbors))
            msg = {
                "logical_clock": self.logical_clock
            }

            self.send_message_to_neighbor(idx, msg)

    def _send_message_to_self():
        self.logical_clock += 1

        msg = {
            "logical_clock": self.logical_clock
        }

        self.send_message_to_self(msg)

