from icmplib import ping
from icmplib import traceroute
from time import ctime
import sys
import ntplib
import socket
import os

IP = "10.0.5.3"
UDP_PORT = 6050

def getTime():
    c = ntplib.NTPClient()
    response = c.request('178.33.203.115', version=3)
    return ctime(response.tx_time)

if __name__ == "__main__":

    ##  IP
    #host = ping(ip, count=10, interval=0.2)
    #print(host)
    #print("---------------")

    ##  TRACEROUTE
    #hops = traceroute(ip)
    #print('Distance/TTL    Address    Average round-trip time')
    #last_distance = 0
    #for hop in hops:
    #    if last_distance + 1 != hop.distance:
    #        print('Some gateways are not responding')

    # See the Hop class for details
    #print(f'{hop.distance}    {hop.address}    {hop.avg_rtt} ms')
    #last_distance = hop.distance

    print("---------------")
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((IP, UDP_PORT))
    #print(socket.gethostbyname(socket.gethostname()))
    while True:
        data, addr = sock.recvfrom(1024)
        data = data.decode('utf-8')
        print("received message: %s" % data)
        if len(data) > 0:
            print(data) 
            time = getTime()
            print("now =", time)
            sent = sock.sendto(time.encode('utf-8'),addr)
            print("SOCKET SENT\n")
            data = ''
