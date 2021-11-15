from datetime import datetime
import socket
from time import *
import _thread
import ntplib
from datetime import datetime
host = '192.168.58.248'  # Standard loopback interface address (localhost)
port = 9998      # Port to listen on (non-privileged ports are > 1023)


def getTime():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    return ctime(response.tx_time).encode('utf-8')
    #tpm = 0
def connect(ip):
    con = bytearray(8)
    con[0] = 0b0
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    #con[5:8] = getTime()
    print(con.decode)
    return con

#tpm = 1
def disconnect(ip):
    dis = bytearray(1)
    dis[0] = 0b1
    array = ip.split(".")

    for a in range(len(array)):
        dis.append(int(array[a]))
    dis.append(bytes(getTime()))
    return dis

#tpm = 2
def error(ip):
    err = bytearray(1)
    err[0] = 0b10
    array = ip.split(".")

    for a in range(len(array)):
        err.append(int(array[a]))
    err.append(bytes(getTime()))
    return err

    
#tpm = 4
def clock_adj(ip):
    c_adj = bytearray(1)
    c_adj[0] = 0b100
    array = ip.split(".")

    for a in range(len(array)):
        c_adj.append(int(array[a]))
    c_adj.append(bytes(getTime()))
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

    ClientSocket.close()

if __name__ == "__main__":
    
    _thread.start_new_thread(serverComm,())

    while 1:
        pass