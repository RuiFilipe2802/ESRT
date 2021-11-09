from icmplib import ping
from icmplib import traceroute
from time import ctime
import sys
import ntplib
import socket

ip = sys.argv[1]
UDP_PORT = 6050

def getTime():
    c = ntplib.NTPClient()
    response = c.request('pt.pool.ntp.org', version=3)
    return ctime(response.tx_time)

def send():
    time = getTime()
    print("now =", time)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(time.encode('utf-8'), (ip, UDP_PORT))
    print("SOCKET SENT\n")

def receive():
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((ip, UDP_PORT))
    while True:
       data, addr = sock.recvfrom(1024)
       print("received message: %s" % data.decode('utf-8'))
       time = getTime()


if __name__ == "__main__":

    ##  IP
    host = ping(ip, count=10, interval=0.2)
    print(host)
    print("---------------")

    ##  TRACEROUTE
    hops = traceroute(ip)
    print('Distance/TTL    Address    Average round-trip time')
    last_distance = 0
    for hop in hops:
        if last_distance + 1 != hop.distance:
            print('Some gateways are not responding')

    # See the Hop class for details
    print(f'{hop.distance}    {hop.address}    {hop.avg_rtt} ms')
    last_distance = hop.distance

    print("---------------")

    choice ='0'
    while choice =='0':
        print("1.   Send")
        print("2.   Receive")

        choice = input("Please make a choice: ")

        if choice == "1":
            send()
        elif choice == "2":
            receive()
        else:
            print("I don't understand your choice.")
