from channels import route_class, route
from packets.consumers import Demultiplexer, device_connect, device_capture, execute_payload, web_connect
from packets.models import PacketBinding, DeviceBinding, HostBinding


channel_routing = [
    route_class(Demultiplexer, path='^/packets/stream/?$'),
    route("binding.pkts", PacketBinding.consumer), # binding where all packets instances are relayed
    route("web.connect", web_connect), # for web interface to connect to
    route("binding.devices", DeviceBinding.consumer), # for keeping the select field up to date
    route("binding.devices.connect", device_connect), # for new capture devices
    route("binding.devices.capture", device_capture), # for starting a new sniff
    route("binding.hosts", HostBinding.consumer), # for new hosts
    route("execute.payload", execute_payload) # for executing payloads
]
