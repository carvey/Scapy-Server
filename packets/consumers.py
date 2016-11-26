from channels.generic.websockets import WebsocketDemultiplexer
from .models import Device, Payload, Host
from channels import Group
import json


class Demultiplexer(WebsocketDemultiplexer):

    mapping = {
        "pkts": "binding.pkts", # binding where all packets instances are relayed
        "web-connect": "web.connect",
        "devices": "binding.devices", # for keeping the select field up to date
        "device_connect": "binding.devices.connect", # for new capture devices
        "capture": "binding.devices.capture", # for starting a new sniff
        'hosts': "binding.hosts", # for new hosts
        'execute': "execute.payload" # for executing payloads
    }

    def connection_groups(self):
        """
        The groups to add all connecting users to
        :return:
        """
        return ["connected-devices"]


def web_connect(message):
    connect = message.content['connect']
    if connect:
        Group("web-connect").add(message.reply_channel)


def device_connect(message):
    data = message.content['data']
    device_name = data['device']
    payloads = data['payloads']
    hosts = data['hosts']

    device = Device.objects.get_or_create(name=device_name)[0]

    Payload.objects.all().delete()
    for payload in payloads:
        Payload.objects.get_or_create(name=payload)

    Host.objects.all().delete()
    for ip, mac in hosts.items():
        Host.objects.get_or_create(mac=mac, ip=ip)

    Group(device_name).add(message.reply_channel)
    print("Connected: %s" % device)

def device_capture(message):
    """
    Used to start or stop a remote capture
    """
    data = message.content['data']
    device_name = data['device']
    capture = data['capture']
    count = data['count']
    scapy_filter = data['scapy_filter']

    payload = {
            'capture': str(capture),
            'count': count,
            'filter': scapy_filter
    }

    Group(device_name).send({
        'text': json.dumps(payload)
    })

def execute_payload(message):
    device = Device.objects.first()
    data = message.content['data']
    remote_payload = data['payload']
    mac = data['mac']
    ip = data['ip']

    payload = {
        'payload': remote_payload,
        'mac': mac,
        'ip': ip
    }

    Group(device.name).send({
        'text': json.dumps(payload)
    })