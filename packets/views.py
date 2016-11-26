from django.shortcuts import render
from .models import Packet, Device, Host, Payload
from django.http import HttpResponse
import json

def packets(request):

    return render(request, "packets.html", {
        "packets": Packet.objects.order_by("timestamp"),
        "devices": Device.objects.filter(connected=True)
    })


def hosts(request):
    return render(request, "hosts.html", {
        'hosts': Host.objects.all(),
        'payloads': Payload.objects.all()
    })


def clear_packets(request):
    Packet.objects.all().delete()
    # Host.objects.all().delete()

    status = {"status": 1}

    if Packet.objects.all().count() == 0 and Host.objects.all().count() == 0:
        status['status'] = 0

    return HttpResponse(json.dumps(status))