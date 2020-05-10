import socket, os, struct, threading, time
from ctypes import *
from netaddr import IPNetwork,IPAddress

class IP(Structure):
    _fields_ = [
            ("ihl", c_ubyte, 4),
            ("version", c_ubyte, 4),
            ("tos", c_ubyte),
            ("len", c_ushort),
            ("id", c_ushort),
            ("offset", c_ushort),
            ("ttl", c_ubyte),
            ("protocol_num", c_ubyte),
            ("sum", c_ushort),
            ("src", c_uint32),
            ("dst", c_uint32)
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

class ICMP(Structure):
    _fields_ = [
            ("type",        c_ubyte),
            ("code",        c_ubyte),
            ("checksum",    c_ushort),
            ("unused",      c_ushort),
            ("next_hop_mtu",c_ushort)
            ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass

subnet = "192.168.178.0/24"

magic_message = "message"

def udp_sender(subnet, magic_message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message, ("{}".format(ip), 65212))
        except:
            pass

t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
t.start()

socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind(("127.0.0.1", 0))

sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

try:
    while True:
        raw_buff = sniffer.recvfrom(65535)[0]
        ip_header = IP(raw_buff[0:20])

        print("protocol {} src {} dst {}".format(ip_header.protocol, ip_header.src_address, ip_header.dst_address))
        if ip_header.protocol == "ICMP":
            offset = ip_header.ihl * 4
            buff = raw_buff[offset:offset + sizeof(ICMP)]

            icmp_header = ICMP(buff)
            if icmp_header.code == 3 and icmp_header.type == 3:
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                    if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message:
                        print("Host up: {}".format(ip_header.src_address))

            #print("ICMP -> Type: {} Code: {}".format(icmp_header.type, icmp_header.code))
except KeyboardInterrupt:
    pass

