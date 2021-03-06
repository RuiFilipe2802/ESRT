from datetime import datetime
import socket
from time import *
import _thread
import ntplib
from datetime import datetime
import sys
import mysql.connector

host = '192.168.58.248'  # Standard loopback interface address (localhost)
port = 9998      # Port to listen on (non-privileged ports are > 1023)
port2 = 5000

ip_source=""
ip_dest1=""
ip_dest2=""
ip_disc=""
            
porta_source=0
porta_dest1=0
porta_dest2=0



def getTime():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    return ctime(int(response.recv_time))
    
#tpm = 0
def connect(ip):
    con = bytearray(1)
    con.append(0b0)
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    con.append(getTime())
    print(con.decode)

    return con

#tpm = 1
def disconnect(ip):
    dis = bytearray(1)
    dis.append(0b1)
    array = ip.split(".")

    for a in range(len(array)):
        dis.append(int(array[a]))
    dis.append(getTime())
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

def package_interpretation(Response):
    if Response[0] == 3:
        for a in range(len(Response[1:4])):
            ip_source=a.join(".")
        for b in range(len(Response[5:8])):
            ip_dest1=b.join(".")
        for c in range(len(Response[9:12])):
            ip_dest2=c.join(".")
        porta_source=Response[13:14]
        porta_dest1=Response[15:16]
        porta_dest2=Response[17:18]
  
#tpm = 4
def clock_adj(ip):
    c_adj = bytearray(1)
    c_adj.append(0b100)
    array = ip.split(".")
    for a in range(len(array)):
        c_adj.append(int(array[a]))
    c_adj.append(getTime())
    return c_adj

def serverComm():

    ClientSocket = socket.socket()
    print('Waiting for connection')
    try:
        ClientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))
    while True:
        #Input = input('Say Something: ')
        packet = connect("192.168.58.25")
        ClientSocket.send(packet)
        Response = ClientSocket.recv(1024)
        print(Response.decode('utf-8'))

        if Response[0] == 3:
            
            for a in range(Response[1:4]):
                ip_source.join(a.join("."))

            for b in range(Response[5:8]):
                ip_dest1.join(b.join("."))

            for c in range(Response[9:12]):
                ip_dest2.join(c.join("."))

        
        if Response[0]==4:
            for a in range(Response[1:4]):
                ip_disc.join(a.join("."))

        
            
    ClientSocket.close()

def peerServer(ip_src,porta_src):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip_src, porta_src))
    print ("waiting on port:", porta_src)
    while 1:
        data, addr = s.recvfrom(1024)
        print(data)

def peerClient(ip_dest,porta_dest):
    # create dgram udp socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ('Failed to create socket')
        sys.exit()

    while(1) :
        msg = bytes('Pouca treta'.encode())
        try :
            #Set the whole string
            s.sendto(msg, (ip_dest, porta_dest))
            # receive data from client (data, addr)
            d = s.recvfrom(1024)
            reply = d[0]
            addr = d[1]
            
            print ('Server reply : ' + reply)
        
        except socket.error :
            print ('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()  



if __name__ == "__main__":

    ip_dest1="192.3.4.6"
    ip_dest2="193.2.1.4"
    porta_dest1=4000
    porta_dest2=5000
    
    #_thread.start_new_thread(serverComm,())
    

    #_thread.start_new_thread(peerServer,(ip_source,porta_source))

    #_thread.start_new_thread(peerClient,(ip_dest1,porta_dest1))
    #_thread.start_new_thread(peerClient,(ip_dest2,porta_dest2))

    while 1:
        pass