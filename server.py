import socket
import os
from _thread import *
import time
import ntplib
from time import ctime

host = '192.168.58.248'  # Standard loopback interface address (localhost)
port = 9998      # Port to listen on (non-privileged ports are > 1023)

def getTime():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    return response.tx_time

#tpm = 3  
def send_neighbors(ip,ip1,ip2,porta,porta1,porta2):
    send=bytearray(1)
    send[0]=0b11
    array = ip.split(".")
    array2 = ip1.split(".")
    array3 = ip2.split(".") 

    for a in range(len(array)):
        send.append(int(array[a]))
    for b in range(len(array2)):
        send.append(int(array2[b]))
    for c in range(len(array3)):
        send.append(int(array3[c]))

    send.append(bytes(getTime()))
    send.append(bytes(porta))
    send.append(bytes(porta1))
    send.append(bytes(porta2))
    return send


def thread_client(connection):
    connection.send(str.encode('Welcome to the Server'))
    while True:
        data = connection.recv(2048)
        #interpretar data de modo a ver o que o peer quer fazer, ou conectar ou desconectar
        if not data:
            break
        if data[0] == 0:
            print(data)
            connection.sendall(send_neighbors("120.20","121.1","122.2",5,4,3))
        #elif data[0] == 1:
    connection.close()

if __name__ == "__main__":
    '''with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                int_val = []
                for i in range(len(data)):
                    int_val.append(int(data[i]))
                print(int_val)
                if not data:
                    break
                conn.sendall(data)'''
    ServerSocket = socket.socket()
    ThreadCount = 0
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
    