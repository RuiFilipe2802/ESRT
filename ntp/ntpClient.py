from icmplib import ping
from icmplib import traceroute
from time import ctime
import sys
import ntplib
import socket
import os

IP = "10.0.5.3"
UDP_PORT = 6050

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto("boas".encode('utf-8'), (IP, UDP_PORT))
    print("boas")

    data, addr = sock.recvfrom(1024)
    print("received message: %s" % data.decode('utf-8'))
