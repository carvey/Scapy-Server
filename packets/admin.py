from django.contrib import admin
from .models import Packet


admin.site.register(
    Packet,
    list_display=["id", "timestamp", "packet"],
)
