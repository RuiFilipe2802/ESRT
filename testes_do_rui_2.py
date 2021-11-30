from datetime import date, datetime
import socket
from time import *
import time
import _thread
import ntplib
from datetime import datetime
import sys
import os
import struct

host = '10.0.5.3'  # Standard loopback interface address (localhost)
port = 9999      # Port to listen on (non-privileged ports are > 1023)
port2 = 5000

ip_source=""
ip_dest1=""
ip_dest2=""
ip_disc=""
            
porta_source=5001
porta_dest1=0
porta_dest2=0

ip_dest1="10.0.1.2"
porta_dest1 = 5005

'''mydb = mysql.connector.connect(
  host='localhost',
  user="root",
  password="1234",
)

cur = mydb.cursor()

cur.execute("CREATE DATABASE peer_table IF NOT EXIST")
cur.execute("CREATE TABLE routing_table (ip_Dest VARCHAR(255),port VARCHAR(255), prox VARCHAR(255)")
'''

def getTime():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    return ctime(int(response.recv_time))

def setTime():
    c = ntplib.NTPClient() 
    response = c.request ('pool.ntp.org') 
    ts = response.tx_time 
    _date = time.strftime ('%y-%m-%d ' , time.localtime(ts)) 
    os.system('date --set='+_date)
    _time = time.strftime('%H:%M:%S', time.localtime(ts))
    t = datetime.fromtimestamp(response.orig_time) 
    #_time = t.strftime("%H:%M:%S.%f")
    os.system('date +%T -s "'+_time+'"')
    #os.system('date +%FT%T.%3N')
    
#tpm = 0
def connect(ip):
    con = bytearray(1)
    con[0] = (0b0)
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    #con.append(getTime())
    #print(con.decode)
    return con

#tpm = 1
def disconnect(ip):
    dis = bytearray(1)
    dis[0]=(0b1)
    array = ip.split(".")
    for a in range(len(array)):
        dis.append(int(array[a]))
    #dis.append(getTime())
    return dis

#tpm = 2
def error(ip):
    err = bytearray(1)
    err.append(0b10)
    array = ip.split(".")
    for a in range(len(array)):
        err.append(int(array[a]))
    err.append(getTime())
    return err

def package_interpretation(response):
    if response[0] == 3:
        for a in range(len(response[1:4])):
            ip_source=a.join(".")
        for b in range(len(response[5:8])):
            ip_dest1=b.join(".")
        for c in range(len(response[9:12])):
            ip_dest2=c.join(".")
        porta_source=response[13:14]
        porta_dest1=response[15:16]
        porta_dest2=response[17:18]
  
#tpm = 4
def clock_adj(ip):
    c_adj = bytearray(1)
    c_adj.append(0b100)
    array = ip.split(".")
    for a in range(len(array)):
        c_adj.append(int(array[a]))
    c_adj.append(getTime())
    return c_adj

#tpm = 6
def timeCalc(ip):
    now = datetime.now()
    timeStamp = float(now.utcnow().timestamp())
    buf = bytearray(struct.pack('f', timeStamp))
    con = bytearray(1)
    con[0] = (0b110)
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    con.extend(buf)
    print(con)
    print("-------------------------------")
    return con

def serverComm():
    ClientSocket = socket.socket()
    print('Waiting for connection')
    try:
        ClientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))
    ipOrigin = ClientSocket.getsockname()[0]
    ip_source = ipOrigin

    _thread.start_new_thread(peerServer,(ip_source,porta_source))
    #_thread.start_new_thread(peerClient,(ip_dest1,porta_dest1))
    #_thread.start_new_thread(peerClient,(ip_dest2,porta_dest2))

    while True:
        #Input = input('Say Something: ')
        packet = connect(ipOrigin)
        ClientSocket.send(packet)
        Response = ClientSocket.recv(1024)
        print(Response.decode('utf-8'))
        packet = disconnect(ipOrigin)
        ClientSocket.send(packet)
        Response = ClientSocket.recv(1024)
        print(Response.decode('utf-8'))
        sleep(2)

        '''if Response[0] == 3:
            for a in range(Response[1:4]):
                ip_source.join(a.join("."))
            for b in range(Response[5:8]):
                ip_dest1.join(b.join("."))
            for c in range(Response[9:12]):
                ip_dest2.join(c.join("."))
            for d in range(Response[13:14]):
                porta_source.join(d)
            for e in range(Response[15:16]):
                porta_dest1.join(e)
            for f in range(Response[17:18]):
                porta_dest2.join(f) 

        if Response[0]==4:
            for a in range(Response[1:4]):
                ip_disc.join(a.join("."))'''
            
    ClientSocket.close()

def peerServer(ip_src,porta_src):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(porta_src)
    print('.........')
    print("À ESPERA..................")
    s.bind((ip_src, porta_src))
    print ("waiting on port:", porta_src)
    while 1:
        data, addr = s.recvfrom(1024)
        print(data)

def peerClient(ip_dest,porta_dest):
    # create dgram udp socket
    print('ESTOU AQUI')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ('Failed to create socket')
        sys.exit()
    while(1) :
        msg = (timeCalc(ip_dest))
        #msg = bytes('Pouca treta'.encode())
        #print(msg)
        try :
            #Set the whole string
            s.sendto(msg, (ip_dest,porta_dest))
            print("ESTOU AQUI")
            # receive data from client (data, addr)
            d = s.recvfrom(1024)
            reply = d[0]
            addr = d[1]
            print ('Server reply : ' + reply)
        
        except socket.error :
            print ('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()  

'''def create_DB():
    cur.execute("INSERT INTO routing_table(ip_Dest, port) VALUES(%s,%s)",(ip_dest1,porta_dest1))
    cur.execute("INSERT INTO routing_table(ip_Dest, port) VALUES(%s,%s)",(ip_dest2,porta_dest2))
    #mydb.commit()

def update_DB():
    if (cur.execute("SELECT * FROM routing_table WHERE ip_Dest=%s",ip_disc)):
        cur.execute("DELETE FROM routing_table WHERE ip_Dest=%s",ip_disc)
        mydb.commit()'''
sendTo = 0

def ola(ip):
    while(1):
        sleep(1)
        print("ola")
        print(ip)

def timeCalc():
    now = datetime.now()
    timeStamp = float(now.timestamp())
    inteiro = int(timeStamp)
    decimal = timeStamp - inteiro
    print(decimal)
    print(inteiro)
    timeCal = bytearray(0)
    b_p = inteiro.to_bytes(4,'big')
    for i in range(len(b_p)):
        timeCal.append(b_p[i])
    buf = bytearray(struct.pack('>f', decimal))
    #timeCal[0] = (0b110)
    print('pacote')
    for a in range(len(buf)):
        timeCal.append(buf[a])
    return timeCal

if __name__ == "__main__":
    
    packet = timeCalc()
    print(len(packet))
    inteiro = int.from_bytes(packet[:4],'big')
    print(inteiro)
    timestamp = packet[4:]
    buf = struct.unpack('>f', timestamp)
    print(buf)
    aux = str(buf).strip('(').strip(')').strip(',')
    print(aux)
    numero = inteiro + float(str(aux))
    print(numero)
    timestamp= datetime.fromtimestamp(numero).strftime("%S")
    print(timestamp)


    while(1):            
        pass
