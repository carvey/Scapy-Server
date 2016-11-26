from django.apps import AppConfig


class PacketsConfig(AppConfig):
    name = 'packets'

    def ready(self):
        from packets.signals import save_host
