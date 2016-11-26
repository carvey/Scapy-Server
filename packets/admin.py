from django.contrib import admin
from .models import Packet, Device, Payload, Host


admin.site.register(
    Packet,
    list_display=["id", "timestamp", "packet"],
)

admin.site.register(
    Device,
    list_display=["name", "connected"]
)

admin.site.register(
    Payload,
    list_display=['name']
)

admin.site.register(
    Host,
    list_display=['mac', 'ip']
)