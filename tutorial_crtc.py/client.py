from datetime import datetime
import socket
from time import *
import _thread
import ntplib
from datetime import datetime
import sys
import mysql.connector

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9998      # Port to listen on (non-privileged ports are > 1023)
port2 = 5000


def serverComm():
    ClientSocket = socket.socket()
    print('Waiting for connection')
    try:
        ClientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))
    while True:
        #ClientSocket.send(b'ola')
        #Input = input('Say Something: ')
        print("Ola")
        sleep(2)
        ClientSocket.send(b'')
        print("ja enviei")
        sleep(10)
        ClientSocket.close()
        
            
    ClientSocket.close()



if __name__ == "__main__":

    ip_dest1="192.3.4.6"
    ip_dest2="193.2.1.4"
    porta_dest1=4000
    porta_dest2=5000
    
    _thread.start_new_thread(serverComm,())

    while 1:
        pass