class Channel(object):
    def __init__(self):
        self.messages = []
        self.is_recording = True

    def add_message(self, message):
        if self.is_recording:
            self.messages.append(message)

