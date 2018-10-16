class Message(object):
    def __init__(self, sender, receiver, data):
        self.sender = sender
        self.receiver = receiver
        self.data = data

    def get_channel(self):
        return (self.sender, self.receiver)

