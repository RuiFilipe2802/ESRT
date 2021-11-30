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

PORT = 5000

#   Conf
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT_TCP = 9999         # Port to listen on (non-privileged ports are > 1023)
PORT_UDP = 5000

#   IP Addresses
ip_source=""
ip_disc=""

#   Variáveis globais partilhadas
sendToNeighbours = 0

#   Set time according to NTP Server
def setTime():
    c = ntplib.NTPClient() 
    response = c.request ('pool.ntp.org') 
    ts = response.tx_time 
    _date = time.strftime ('%y-%m-%d ' , time.localtime(ts)) 
    os.system('date --set='+_date)
    _time = time.strftime('%H:%M:%S', time.localtime(ts))
    t = datetime.fromtimestamp(response.orig_time) 
    os.system('date +%T -s "'+_time+'"')
    
#   Connect Peer-Server TYPE 0
def connect(ip):
    now = datetime.now()
    con = bytearray(1)
    con[0] = (0b0)
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    timeStamp = float(now.utcnow().timestamp())
    buf = bytearray(struct.pack('f', timeStamp))
    con.extend(buf)
    return con

#   Disconnect Peer-Server TYPE 1 
def disconnect(ip):
    now = datetime.now()
    dis = bytearray(1)
    dis[0]=(0b1)
    array = ip.split(".")
    for a in range(len(array)):
        dis.append(int(array[a]))
    timeStamp = float(now.utcnow().timestamp())
    buf = bytearray(struct.pack('f', timeStamp))
    dis.extend(buf)
    return dis

#tpm = 2
def error(ip):
    now = datetime.now()
    err = bytearray(1)
    err.append(0b10)
    array = ip.split(".")
    for a in range(len(array)):
        err.append(int(array[a]))
    timeStamp = float(now.utcnow().timestamp())
    buf = bytearray(struct.pack('f', timeStamp))
    err.extend(buf)
    return err

#tpm = 6
def timeCalc(ip):
    now = datetime.now()
    timeStamp = float(now.utcnow().timestamp())
    buf = bytearray(struct.pack('f', timeStamp))
    timeCal = bytearray(1)
    timeCal[0] = (0b110)
    array = ip.split(".")
    for a in range(len(array)):
        timeCal.append(int(array[a]))
    timeCal.extend(buf)
    return timeCal

def serverComm():
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Waiting for connection')
    try:
        ClientSocket.connect((HOST, PORT_TCP))
    except socket.error as e:
        print(str(e))
    ipOrigin = ClientSocket.getsockname()[0]
    ip_source = ipOrigin

    _thread.start_new_thread(peerListener,(ip_source))

    enviar = 0 
    res = 0

    ip_neighbours = []

    while True:
        if(enviar == 0):            # CONNECT
            print('CONNECT')
            packet = connect(ipOrigin)
            ClientSocket.send(packet)
            res = ClientSocket.recv(1024)
            print(res.decode('utf-8'))
        elif(enviar == 1):          # DISCONNECT 
            print('DISCONNECT')
            packet = disconnect(ipOrigin)
            ClientSocket.send(packet)
        elif(enviar == 2):          # ERROR
            print('ERROR')
            packet = error(ipOrigin)
            ClientSocket.send(packet)
        
        if(res[0] == 10):          # Get Neighbours
            nNeighbours = res[1]
            counter = 0
            contador = 0
            while(counter < nNeighbours):
                array4 = res[2+contador:6+contador]
                if(array4 is not ip_neighbours):
                    ip_neighbours.append(socket.inet_ntoa(array4))
                    contador += 4
                    counter += 1
                    _thread.start_new_thread(peerSender,(ip_neighbours[counter],))

            global sendToNeighbours
            sendToNeighbours = 1

        Response = ClientSocket.recv(1024)
        print(Response.decode('utf-8'))
        sleep(2)
            
    ClientSocket.close()

def peerListener(ip_src):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('.........')
    s.bind((ip_src, PORT_UDP))
    print ("waiting on port:", PORT_UDP)
    while 1:
        data, addr = s.recvfrom(1024)
        if(data[0] == 30):            # RECEBE O CUSTO
            array = data[1:5]
            
        elif(data[0] == 31):          # SEND NORMAL DATA
            print('DATA')

def peerSender(ip_dest):
    # create dgram udp socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ('Failed to create socket')
        sys.exit()

    packetType = 20

    while(1) :
        if(packetType == 20):           # ENVIAR CALCULO DO CUSTO
            msg = (timeCalc(ip_dest))
            s.sendto(msg,(ip_dest))
            
        elif(packetType == 21):         # SEND NORMAL DATA
            print('DATA')

if __name__ == "__main__":
    
    setTime()

    _thread.start_new_thread(serverComm,())

    while 1:
        pass
