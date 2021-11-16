from icmplib import ping
from icmplib import traceroute
from time import ctime
import sys
import ntplib
import socket
import os
import time
import datetime
from datetime import datetime
import struct

IP = "10.0.5.2"
UDP_PORT = 6050

if __name__ == "__main__":
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.sendto("boas".encode('utf-8'), (IP, UDP_PORT))
    # print("boas")

    # data, addr = sock.recvfrom(1024)
    # print("received message: %s" % data.decode('utf-8'))
    start = time.time()
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org')
    t = datetime.fromtimestamp(response.tx_time)
    time_ntp = t.strftime("%d %m %H:%M:%S %Y")
    print(time_ntp)
    os.system('date ' +  t.strftime("%x"))
    os.system('time ' +  t.strftime("%X"))
