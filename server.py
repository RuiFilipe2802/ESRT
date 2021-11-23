import socket
import os
from _thread import *
import time
import ntplib
from time import ctime, sleep
import threading
import mysql.connector 

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9999     # Port to listen on (non-privileged ports are > 1023)

variavel_broadcast = 0
lista_mensagens = []
verificar_mensagens = []
lock = threading.Lock()

#pass joao = Johnny1999@

mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "Johnny1999@"
)

mycursor = mydb.cursor()

mycursor.execute("USE server_database")


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

def add_peer_database(id,ip,porta):
    
    mycursor.execute("INSERT INTO peer(id,ip,porta) VALUES (%d,%s,%d)",(id,ip,porta))
    mydb.commit()


def thread_listening(connect, n_t):
    while True:
        data = connect.recv(2048)
        verificar_mensagens[n_t] = 1
        lista_mensagens[n_t] = data
        print(str(lista_mensagens[n_t]) + " numero: "+ str(n_t))


def thread_client(connection,n_thread):
    verificar_mensagens[n_thread] = 0
    start_new_thread(thread_listening,(connection, n_thread,))
    while True:
        #interpretar data de modo a ver o que o peer quer fazer, ou conectar ou desconectar
        #lock.acquire()
        if verificar_mensagens[n_thread] == 1:
            data = lista_mensagens[n_thread]
            if data[0] == 0:
                print("tpm 0")
                connection.send("ola".encode('utf-8'))
                #connection.send(send_neighbors("120.20","121.1","122.2",5,4,3))
                
            elif data[0] == 1:
                print("tpm 1")
                connection.send("ole".encode('utf-8'))
            verificar_mensagens[n_thread] = 0
        #lock.release
            
        if variavel_broadcast == 1:
            #avisar que conectou
            connection.send('mudei esta variavel maltinha')
        if variavel_broadcast == 2:
            #avisar que desconectou
            connection.send('mudei variavel')
    connection.close()

if __name__ == "__main__":
    portas_peer = 5000
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
        add_peer_database(ThreadCount, address[0], portas_peer)
        
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        verificar_mensagens.append(0)
        lista_mensagens.append('')
        start_new_thread(thread_client,(Client, ThreadCount,))
        ThreadCount += 1
        portas_peer +=1
        print('Thread Number: ' + str(ThreadCount))
    ServerSocket.close()
    