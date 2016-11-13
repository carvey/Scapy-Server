from django.db import models
from channels.binding.websockets import WebsocketBinding
from scapy.all import *

# class IntegerValue(models.Model):
#
#     name = models.CharField(max_length=100, unique=True)
#     value = models.IntegerField(default=0)
#
#
# class IntegerValueBinding(WebsocketBinding):
#
#     model = IntegerValue
#     stream = "intval"
#     fields = ["name", "value"]
#
#     @classmethod
#     def group_names(cls, *args, **kwargs):
#         return ["binding.values"]
#
#     def has_permission(self, user, action, pk):
#         return True


class Packet(models.Model):

    timestamp = models.DateTimeField()
    packet = models.TextField(help_text="Stored string representation of a packet")

    def to_python(self):
        return eval(self.packet)

    def summary(self):
        packet = self.to_python()
        return packet.summary()

class PacketBinding(WebsocketBinding):

    model = Packet
    stream = 'pkts'
    fields = ["timestamp", "packet"]

    @classmethod
    def group_names(cls, *args, **kwargs):
        return ["binding.pkts"]

    def has_permission(self, user, action, pk):
        return True
