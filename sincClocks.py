import os 
import time 
import ntplib 
from datetime import datetime

c = ntplib. NTPClient () 
response = c.request ('pool.ntp.org') 
ts = response.tx_time 
_date = time.strftime ('%y-%m-%d ' , time.localtime(ts)) 
os.system('sudo date --set='+_date)
t = datetime.fromtimestamp(response.orig_time) 
_time = t.strftime("%H:%M:%S.%f")
os.system('sudo date +%T -s "'+_time+'"')
os.system('date +%FT%T.%3N')



