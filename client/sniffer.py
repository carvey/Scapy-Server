"""
This file should run on the remote device to send data to the server
Websocket code referenced from: https://pypi.python.org/pypi/websocket-client/

I pulled the logging statement from:
https://pymotw.com/3/threading/
"""

from scapy.all import *
from websocket import create_connection
import argparse
import json
import datetime
import importlib
import logging
import threading
import ipaddress
import netifaces as ni

# code for getting local ip address found at:
# http://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
ni.ifaddresses('en0')
addresses = ni.ifaddresses('en0')
local_ip = addresses[2][0]['addr']
netmask = addresses[2][0]['netmask']

parser = argparse.ArgumentParser("Pass in the remote server info")
parser.add_argument("--server", type=str, required=True, help="URL of the remote server. EX: 'ws://echo.websocket.org/'")
parser.add_argument("--streamurl", type=str, required=True, help="URL of the Django Channel Stream to join")

options = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
)

class WSWrapper:
    """
    Very light wrapper around the websocket and scapy modules, simply for organizational purposes while I
    figure out what needs to be done on this script.
    """

    def __init__(self, url):
        self.conn = create_connection(url)
        self.payloads = {}

        self.listener_thread = None
        self.capture_threads = {}

    def setup(self):
        self.send_connect()
        self.handle_listen()
        self.listener_thread.join()

    def handle_message(self, message):
        data = json.loads(message)
        capture = bool(data.get('capture', None))
        payload = data.get('payload')

        if capture:
            count = data.get('count', None)
            scapy_filter = data.get('filter', None)
            if bool(capture):
                self.handle_capture(count=count, scapy_filter=scapy_filter)

        elif payload:
            self.handle_payload(data=data)

    def handle_listen(self):

        def listen():
            logging.debug("Starting Listener...")
            while True:
                message = self.conn.recv()
                self.handle_message(message)
            logging.debug("Stopping Listen")

        listener = threading.Thread(name="listener daemon", target=listen, daemon=True)
        self.listener_thread = listener
        listener.start()

    def handle_capture(self, **kwargs):
        """
        A message telling the client to capture was received.

        Start up a listener thread
        :return:
        """

        def capture_worker(count=0, scapy_filter=""):
            logging.debug("Starting Capture")
            logging.debug("Capturing...")
            logging.debug("Starting sniff of %s packets with filter of: %s" % (count, scapy_filter))
            self.sniff(count=count, filter=scapy_filter)
            logging.debug("Stopping Capture")

        worker = threading.Thread(name="Capture Worker", target=capture_worker, kwargs=kwargs)
        self.capture_threads[worker.getName()] = worker
        worker.start()

    def handle_payload(self, **kwargs):
        """
        A message telling the client to run a payload was received.

        Start the payload in a new thread.
        :return:
        """

        def payload(data):
            mac = data.get('mac')
            ip = data.get('ip')
            payload = data.get('payload')
            payload_func = self.payloads[payload]

            # strip off any spaces from the ip
            ip = ip.strip()
            mac = mac.strip()

            logging.debug("Running payload: '%s' on host: %s" % (payload, ip))
            # run the payload!
            payload_func(ip=ip, mac=mac)
            logging.debug("Payload: '%s' on host: %s" % (payload_func, ip))

        worker = threading.Thread(name="Capture Worker", target=payload, kwargs=kwargs)
        worker.start()

    def gather_hosts(self):
        ip_addr = ipaddress.IPv4Interface(local_ip + '/' + netmask)
        network_addr = ip_addr.network.with_prefixlen
        logging.debug("Scanning for active hosts on: %s" % network_addr)
        active_hosts = arping(network_addr, verbose=False)

        hosts = {}
        for sent_packet, received_packet in active_hosts[0].res:
            hosts[received_packet.psrc] = received_packet.src

        return hosts

    def send_connect(self):
        payloads_module = importlib.import_module('payloads')
        payloads = payloads_module.registered

        hosts = self.gather_hosts()

        connect_device = {
            'stream': 'device_connect',
            'payload': {
                'data': {
                    'device': "remoteCapture",
                    'payloads': list(payloads.keys()),
                    'hosts': hosts
                }
            }
        }

        connect = json.dumps(connect_device)
        self.conn.send(connect)

        self.payloads.update(payloads)

        # print("Sent Connect Message: %s" % connect)


    def close(self):
        self.conn.close()


    def sniff(self, count, filter=""):

        def send_packet(pkt):

            data = {
                'stream': 'pkts',
                'payload': {
                    'action': 'create',
                    'data': {
                        'packet': pkt.command(),
                        'timestamp': str(datetime.datetime.now())
                    }
                }
            }

            self.conn.send(json.dumps(data))

            # print("Sent: %s" % data)

        sniff(count=count, prn=send_packet, filter=filter)


server_url = "%s/%s" % (options.server, "packets/stream/")
conn = WSWrapper(server_url)
conn.setup()

# conn.sniff()

conn.close()
