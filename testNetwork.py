from icmplib import ping
from icmplib import traceroute
import sys

ip = sys.argv[1]
host = ping(ip, count=10, interval=0.2)
print(host)
print("---------------")
hops = traceroute(ip)
print('Distance/TTL    Address    Average round-trip time')
last_distance = 0
for hop in hops:
    if last_distance + 1 != hop.distance:
        print('Some gateways are not responding')

    # See the Hop class for details
    print(f'{hop.distance}    {hop.address}    {hop.avg_rtt} ms')
    last_distance = hop.distance

