from django.shortcuts import render
from .models import Packet


def index(request):
    """
    Root page view. Just shows a list of values currently available.
    """
    return render(request, "index.html", {

    })

def packets(request):

    return render(request, "packets.html", {
        "packets": Packet.objects.order_by("timestamp"),
    })
