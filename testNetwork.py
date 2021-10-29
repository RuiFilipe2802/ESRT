from icmplib import ping
from icmplib import traceroute
from time import ctime
from datetime import datetime
import sys
import ntplib

ip = sys.argv[1]
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
##  LATENCY
c = ntplib.NTPClient()
response = c.request('europe.pool.ntp.org', version=3)
print(ctime(response.tx_time))
now = datetime. now(). time()
print("now =", now)