from channels.generic.websockets import WebsocketDemultiplexer


class Demultiplexer(WebsocketDemultiplexer):

    mapping = {
        "pkts": "binding.pkts",
    }

    def connection_groups(self):
        return ["binding.pkts"]
