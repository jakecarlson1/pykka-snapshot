from snapshotting import SnapshotableActor
import numpy as np
import time

class Incrementor(SnapshotableActor):
    def __init__(self, msg_send_prob):
        super().__init__()
        self.logical_clock = 0
        self.msg_send_prob = msg_send_prob

    def on_receive(self, message):
        print(message["obj"])
        super_handled_msg = super().on_receive(message)

        if not super_handled_msg:
            self.logical_clock = max(message["obj"]["logical_clock"], self.logical_clock) + 1

            self._print_clock()

            self._can_send_message_to_neighbor()

            self._send_message_to_self()

            time.sleep(1)

    def _can_send_message_to_neighbor(self):
        val = np.random.random_sample()
        if val >= self.msg_send_prob:
            self.logical_clock += 1

            idx = np.random.randint(0, len(self.neighbors))
            msg = {
                "logical_clock": self.logical_clock
            }

            self.send_message_to_neighbor(idx, msg)

    def _send_message_to_self(self):
        self.logical_clock += 1

        msg = {
            "logical_clock": self.logical_clock
        }

        self.send_message_to_self(msg)

    def _print_clock(self):
        print("Clock at", self.id_short, ":", self.logical_clock)

