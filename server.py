import socket
import os
from _thread import *
import time
import ntplib
from time import ctime, sleep

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9999     # Port to listen on (non-privileged ports are > 1023)

varialvel_broadcast = 0

def getTime():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    return response.tx_time

#tpm = 3  
def send_neighbors(ip,ip1,ip2,porta,porta1,porta2):
    send = bytearray(1)
    send.append(3)
    array = ip.split(".")
    array2 = ip1.split(".")
    array3 = ip2.split(".")

    for a in range(len(array)):
        send.append(int(array[a]))
    for b in range(len(array2)):
        send.append(int(array2[b]))
    for c in range(len(array3)):
        send.append(int(array3[c]))

    #send.append((getTime()))
    send.append((porta))
    send.append((porta1))
    send.append((porta2))
    return send

#tpm 4
def connection_ended(ip):
    c_end = bytearray(1)
    c_end.append(4)
    array = ip.split(".")

    for a in range(len(array)):
        c_end.append(int(array[a]))
    
    return c_end

#tpm 5
def warning_con_end(ip):
    con_ended = bytearray(1)
    con_ended.append(5)
    array = ip.split(".")

    for a in range(len(array)):
        con_ended.append(int(array[a]))


def thread_client(connection):
    connection.send(str.encode('Welcome to the Server'))
    data = connection.recv(2048)
    while True:
        data = connection.recv(2048)
        #interpretar data de modo a ver o que o peer quer fazer, ou conectar ou desconectar
        if data[0] == 0:
            connection.send(send_neighbors("120.20","121.1","122.2",5,4,3))
        elif data[0] == 1:
            connection.send()
        if varialvel_broadcast == 1:
            connection.send(connection_ended('127.0.0.1'))
            break
    connection.close()

if __name__ == "__main__":
    ServerSocket = socket.socket()
    ThreadCount = 0
    #ServerSocket.setblocking(0)
    #ServerSocket.settimeout(4)
    try:
        ServerSocket.bind((host,port))
        
    except socket.error as e:
        print(str(e))
    print('Waiting for Connection')
    ServerSocket.listen(5)

    while True:
        Client, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        start_new_thread(thread_client,(Client, ))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    ServerSocket.close()
    