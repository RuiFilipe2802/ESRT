import socket
import select
import _thread
from multiprocessing import Process, Lock
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

msg = []

def socket_server():
    print('Non Blocking - creating socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Non Blocking - connecting')
    ret = s.connect_ex(('localhost',5000)) #BLOCKING

    if ret != 0:
        print('Non Blocking - failed to connect!')
    
    print('Non Blocking - connected!')
    s.setblocking(False)

    inputs = [s]
    outputs = [s]
    while inputs:
        #print('Non Blocking - waiting...')
        global msg
        readable,writable,exceptional = select.select(inputs,outputs,inputs,0.5)
        for s in writable:
            #print("Escrever")
            if(len(msg)> 0):
                msg = msg.encode()
                byte_array = bytearray(msg)
                print('Non Blocking - sending...')
                data = s.send(byte_array)
                print(f'Non Blocking - sent: {data}')
                msg = []
                print(msg)

        for s in readable:
            #print(f'Non Blocking - reading...')
            data = s.recv(1024)
            print(f'Non Blocking - data: {data}')
 

        for s in exceptional:
            inputs.remove(s)
            outputs.remove(s)
            break

def fun_input():
    while 1:
        global msg
        msg = input()
        print('Input: '+msg)

if __name__ == "__main__":
    
    _thread.start_new_thread(socket_server,())
    _thread.start_new_thread(fun_input,())
    while 1:
        pass
    