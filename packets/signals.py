from django.db.models.signals import post_save
from .models import Packet, Host
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

def local_address(address):
    addr = address.split(".")
    octet1 = int(addr[0])
    if octet1 == 10 or octet1 == 172 or octet1 == 192:
        return True

    return False


# @receiver(post_save, sender=Packet)
def save_host(sender, instance, created, **kwargs):
    if created:

        host = None

        mac = instance.src_mac()
        ip = instance.src_ip()

        if ip:
            if not local_address(ip):
                mac = instance.dst_mac()
                ip = instance.dst_ip()

        if mac:
            if ip: # if true, both mac and ip are present
                if local_address(ip): # if true, this ip is a local one that we can record
                    try: # get a host and add an ip
                        host = Host.objects.get(mac=mac)
                        host.ip = ip
                        host.save()

                    except ObjectDoesNotExist: # no host with this mac exists
                        host = Host(mac=mac)
                        host.ip = ip
                        host.save()

            else:
                try: # check to see if a host exists for this mac. If so, were all good
                    host = Host.objects.get(mac=mac)

                except ObjectDoesNotExist: # no host with this mac exists
                    host = Host(mac=mac)
                    host.save()
