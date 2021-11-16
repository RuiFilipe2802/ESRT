import os 
import time 
import ntplib 
c = ntplib. NTPClient () 
response = c.request ('pool.ntp.org') 
ts = response.tx_time 
_date = time.strftime ('%y-%m-%d ' , time.localtime(ts)) 
_time = time.strftime ('%H:%M:%S', time.localtime(ts)) 
os.system('sudo date --set='+_date+'&& sudo date +%T -s "'+_time+'"')

