from django.db import models
from channels.binding.websockets import WebsocketBinding
from scapy.layers.all import *


class Packet(models.Model):

    timestamp = models.DateTimeField(auto_now_add=True)
    packet = models.TextField(help_text="Stored string representation of a packet")

    def to_python(self):
        return eval(self.packet)

    def summary(self):
        packet = self.to_python()
        return packet.summary()

    def ip(self):
        packet = self.to_python()

        if packet.haslayer(IP):
            src = packet[IP].src
            dst = packet[IP].dst
            return (src, dst)

        return ("", "")

    def mac(self):
        packet = self.to_python()

        if packet.haslayer(Ether):
            src = packet[Ether].src
            dst = packet[Ether].dst
            return (src, dst)

        elif packet.haslayer(Dot3):
            src = packet[Dot3].src
            dst = packet[Dot3].dst
            return (src, dst)

        return ("", "")

    def src_ip(self):
        ips = self.ip()
        return ips[0]

    def dst_ip(self):
        ips = self.ip()
        return ips[1]

    def src_mac(self):
        macs = self.mac()
        return macs[0]

    def dst_mac(self):
        macs = self.mac()
        return macs[1]

    def protocol(self):
        packet = self.to_python()
        proto = packet.lastlayer().name
        if proto == 'Raw':
            proto = packet.payload
            while proto.payload.name != 'Raw':
                proto = proto.payload

            proto = proto.name

        return proto


class PacketBinding(WebsocketBinding):

    model = Packet
    stream = 'pkts'
    fields = ["timestamp", "packet"]
    serialized_methods = {
        "src_mac": Packet.src_mac,
        "dst_mac": Packet.dst_mac,
        "src_ip": Packet.src_ip,
        "dst_ip": Packet.dst_ip,
        "proto": Packet.protocol,
        "summary": Packet.summary
    }

    @classmethod
    def group_names(cls, *args, **kwargs):
        return ["web-connect"]

    def has_permission(self, user, action, pk):
        return True

    def serialize(self, instance, action):
        payload = super(PacketBinding, self).serialize(instance, action)
        serialized_methods = self.serialized_method_data(instance)

        payload.update(serialized_methods)

        return payload

    def serialized_method_data(self, instance):
        payload = {}
        for name, method in self.serialized_methods.items():
            payload[name] = method(instance)

        return payload


class Payload(models.Model):

    name = models.CharField(max_length=256)

class Device(models.Model):

    name = models.CharField(max_length=50)
    connected = models.BooleanField(default=True)
    payloads = models.ManyToManyField(Payload, blank=True, null=True)

class DeviceBinding(WebsocketBinding):

    model = Device
    stream = "pkts"
    fields = ["name", "connected", "payloads"]

    @classmethod
    def group_names(cls, *args, **kwargs):
        return ["binding.devices"]

    def has_permission(self, user, action, pk):
        return True


class Host(models.Model):

    mac = models.CharField(max_length=50, null=True)
    ip = models.CharField(max_length=50, null=True, unique=True)


class HostBinding(WebsocketBinding):

    model = Host
    stream = "hosts"
    fields = ["mac", "ip"]

    @classmethod
    def group_names(cls, *args, **kwargs):
        return ["web-connect"]

    def has_permission(self, user, action, pk):
        return True
