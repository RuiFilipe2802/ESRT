import os 
import time 
import ntplib 
c = ntplib. NTPClient () 
response = c.request ('88.157.128.22') 
ts = response.tx_time 
_date = time.strftime ('%y-%m-%d ' , time.localtime(ts)) 
_time = time.strftime ('%H:%M:%S', time.localtime(ts)) 
os.system('date --set='+_date+'&& date +%T -s "'+_time+'"')

