class Channel(object):
    def __init__(self):
        self.messages = []
        self.is_recording = True

    def add_message(self, message):
        self.messages.append(message)

