import socket
import random
from _thread import *
import time
import ntplib
from time import ctime, sleep
import threading
import mysql.connector 

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9999     # Port to listen on (non-privileged ports are > 1023)

#qnt de vizinhos atribuidos a peer
N = 2
variavel_broadcast = 0
lista_mensagens = []
verificar_mensagens = []
lock = threading.Lock()
N_thread = 0
threadCount = 0

#pass joao = Johnny1999@

mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "Johnny1999@",
  database = "server_database"
)

mycursor = mydb.cursor()



def getTime():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    return response.tx_time

#tpm = 3  
def send_neighbors(porta,n_peers,n_vizinhos,ip1,porta1,ip2,porta2):
    send = bytearray(1)
    send[0] = 3
    #send.append(ip1.encode())
    array2 = ip1.split(".")
    array3 = ip2.split(".")
    b_p = porta.to_bytes(2,'big')
    for i in range(len(b_p)):
        send.append(i)

    send.append(n_peers)
    send.append(n_vizinhos)

    for b in range(len(array2)):
        send.append(int(array2[b]))
    
    b_p1 = porta1.to_bytes(2,'big')
    for i in range(len(b_p1)):
        send.append(i)
    
    for c in range(len(array3)):
        send.append(int(array3[c]))

    b_p2 = porta2.to_bytes(2,'big')
    
    for i in range(len(b_p2)):
        send.append(i)

    print(send)
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
def starting_peer(ip):
    con_ended = bytearray(1)
    con_ended.append(5)
    array = ip.split(".")

    for a in range(len(array)):
        con_ended.append(int(array[a]))

def add_peer_database(id,ip,porta):
    mycursor.execute("INSERT INTO peer(id,ip,porta) VALUES (%s,%s,%s)",(id,ip,porta))
    mydb.commit()

def atribuir_vizinhos(id):
    numero_ids = []
    print(threadCount)
    if threadCount == 2:
        if id == 0:
            print("vou adicionar 1")
            numero_ids.append(1)
            print(numero_ids)
            return numero_ids
        else:
            print("vou adicionar 0")
            numero_ids.append(0)
            print(numero_ids)
            return numero_ids
    else:
        for a in range(N):
            b = random.randint(0,threadCount)
            if b != id and b not in numero_ids:
                numero_ids.append(b)
            else: 
                a = a - 1
        return numero_ids

def thread_listening(connect, n_t):
    while True:
        data = connect.recv(2048)
        if threadCount == 1 and data[0] == 0:
            print("enviar mensagem para esperar por peers")
        else:
            verificar_mensagens[n_t] = 1
            lista_mensagens[n_t] = data
            print(str(lista_mensagens[n_t]) + " numero: "+ str(n_t))


def thread_client(connection,n_thread, listening_port):
    verificar_mensagens[n_thread] = 0
    start_new_thread(thread_listening,(connection, n_thread,))
    while True:
        #interpretar data de modo a ver o que o peer quer fazer, ou conectar ou desconectar
        #lock.acquire()
        if verificar_mensagens[n_thread] == 1:
            data = lista_mensagens[n_thread]
            if data[0] == 0:
                print("tpm 0")
                viz_ids = []
                viz_ids = atribuir_vizinhos(n_thread)
                print("vizinhos: "+ str(viz_ids))
                if viz_ids is None:
                    print("Esperar por mais conexões para iniciar rede overlay vizinhos")
                else: 
                    if threadCount == 2:
                        #enviar apenas um vizinho, o 2 ip vai com 0.0.0.0 e porta a 0
                        sql = "SELECT ip FROM peer WHERE id = "+str(viz_ids[0])+""
                        mycursor.execute(sql)
                        aux = mycursor.fetchall()
                        aux1 = str(aux[0])
                        ip1 = aux1.strip("[").strip("(").strip("'").strip(")").strip("]").strip(",").strip("'")
                        print(ip1)
                        sql = "SELECT porta FROM peer WHERE id = "+str(viz_ids[0])+""
                        mycursor.execute(sql)
                        aux = mycursor.fetchall()
                        aux1 = str(aux[0])
                        porta = int(aux1.strip("[").strip("(").strip("'").strip(")").strip("]").strip(","))
                        print(porta)
                        packet = send_neighbors(listening_port,threadCount,1, ip1, porta, '0', 0)
                    else:
                        sql = "SELECT ip FROM peer WHERE id = "+str(viz_ids[0])+""
                        mycursor.execute(sql)
                        aux = mycursor.fetchall()
                        aux1 = str(aux[0])
                        ip1 = aux1.strip("[").strip("(").strip("'").strip(")").strip("]").strip(",").strip("'")
                        print(ip1)
                        sql = "SELECT ip FROM peer WHERE id = "+str(viz_ids[0])+""
                        mycursor.execute(sql)
                        aux = mycursor.fetchall()
                        aux1 = str(aux[0])
                        ip2 = aux1.strip("[").strip("(").strip("'").strip(")").strip("]").strip(",").strip("'")
                        sql = "SELECT porta FROM peer WHERE id = "+str(viz_ids[0])+""
                        mycursor.execute(sql)
                        aux = mycursor.fetchall()
                        aux1 = str(aux[0])
                        porta1 = int(aux1.strip("[").strip("(").strip(")").strip("]").strip(","))
                        sql = "SELECT porta FROM peer WHERE id = "+str(viz_ids[0])+""
                        mycursor.execute(sql)
                        aux = mycursor.fetchall()
                        aux1 = str(aux[0])
                        porta2 = int(aux1.strip("[").strip("(").strip(")").strip("]").strip(","))
                        packet = send_neighbors(listening_port,threadCount,N, ip1, porta1,ip2,porta2)

                #connection.send(send_neighbors("120.20","121.1","122.2",5,4,3))
                connection.send(packet)
            elif data[0] == 1:
                print("tpm 1")
                connection.send("ole".encode('utf-8'))
            verificar_mensagens[n_thread] = 0
            print("passei aqui")
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
    #threadCount = 0
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
        add_peer_database(threadCount, address[0], portas_peer)
        
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        verificar_mensagens.append(0)
        lista_mensagens.append('')
        start_new_thread(thread_client,(Client, threadCount,portas_peer,))
        threadCount += 1
        portas_peer +=1
        print('Thread Number: ' + str(threadCount))
    ServerSocket.close()
    