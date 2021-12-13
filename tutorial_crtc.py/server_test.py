import socket
import struct
import random
from _thread import *
import _thread
import time
import ntplib
from time import ctime, sleep
import threading
import mysql.connector
import struct
import sqlite3
from sqlite3 import Error

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9999

verificar_mensagens = 0
lista_mensagens = []


def thread_listening(connect, n_t):
    global verificar_mensagens
    lista_mensagens.append("")
    print("lets start2")
    while True:
        #print("vou ouvir: "+str(n_t))
        try:
            data = connect.recv(2048)
            print('DATA : ' + str(data))
            print('\n')
            lista_mensagens[0] = data
            verificar_mensagens = 1

        except socket.error:
            print("crt c na listening")
            break
        #print("liberado ouvi :"+str(n_t))
        #print(str(lista_mensagens[n_t]) + " numero: "+ str(n_t))
    print("sai do fechei a socket" )


def thread_client(connection,n_thread, listening_port):
    global verificar_mensagens
    start_new_thread(thread_listening,(connection, n_thread,))
    print("lets start")
    while True:
        #interpretar data de modo a ver o que o peer quer fazer, ou conectar ou desconectar
        if verificar_mensagens == 1:
            print(lista_mensagens[0])
            data = lista_mensagens[0]
            print(lista_mensagens[0])
            print(data)
            verificar_mensagens = 0
            if data[0] == 25:
                break
    print("sai do while true" )
    connection.close()


if __name__ == "__main__":
    portas_peer = 5000
    threadCount = 0
    ServerSocket = socket.socket()
    
    try:
        ServerSocket.bind((host,port))
        
    except socket.error as e:
        print(str(e))
    print('Waiting for Connection')
    ServerSocket.listen(5)

    while True:
        Client, address = ServerSocket.accept()
        
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        start_new_thread(thread_client,(Client, threadCount,portas_peer,))
        threadCount += 1
        portas_peer +=1
        print('Thread Number: ' + str(threadCount))
    ServerSocket.close()