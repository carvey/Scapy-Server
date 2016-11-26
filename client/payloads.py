from scapy.all import *
import netifaces as ni

# code for getting local ip address found at:
# http://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
ni.ifaddresses('en0')
addresses = ni.ifaddresses('en0')
local_ip = addresses[2][0]['addr']
local_mac = addresses[18][0]['addr']

def ping(ip, mac):
    packet = IP(src=local_ip, dst=ip)/ICMP()
    send(packet)
    print("Sent ping to: %s!" % ip)

def arpcachepoison(ip, mac):
    # found details on the 'op' param found at:
    # http://stackoverflow.com/questions/32804176/python-scapy-arp-request-and-response
    arp_packet = ARP(op=ARP.is_at, hwsrc=local_mac, psrc=local_ip, hwdst=ip)
    response = sr(arp_packet)
    print(response)
    # send(arp_packet)

registered = {
    'ping': ping,
    'arpcachepoison': arpcachepoison
}