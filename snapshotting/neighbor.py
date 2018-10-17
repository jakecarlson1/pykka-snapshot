class Neighbor(object):
    def __init__(self, actor_proxy):
        self.proxy = actor_proxy
        self.ref = self.proxy.actor_ref
        self.id = self.proxy.id.get()
        self.id_short = self.id.split(":")[2].split("-")[0]

