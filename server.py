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
peers_connected = 0

#pass joao = Johnny1999@

mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "johnny1999",
  database = "server_database"
)

mycursor = mydb.cursor()


def getTime():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    return response.tx_time

#tpm = 3  
def send_neighbors(porta, n_vizinhos, ip1, ip2):
    send = bytearray(1)
    send[0] = 3
    #send.append(ip1.encode())
    array2 = ip1.split(".")
    array3 = ip2.split(".")
    
    send.append(n_vizinhos)

    for b in range(len(array2)):
        send.append(int(array2[b]))
    
    for c in range(len(array3)):
        send.append(int(array3[c]))

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
    con_ended[0] = 5
    array = ip.split(".")

    for a in range(len(array)):
        con_ended.append(int(array[a]))


def add_peer_database(id,ip,porta,status):
    mycursor.execute("INSERT INTO peer(id,ip,porta,status) VALUES (%s,%s,%s,%s)",(id,ip,porta,status))
    mydb.commit()

def set_status_on(id):
    sql = "UPDATE peer set status = 1 WHERE id = "+str(id)
    mycursor.execute(sql)
    mydb.commit()

def verificar_status(b):
    print("entrei2")
    sql = "SELECT status FROM peer WHERE id = "+str(b)+""
    mycursor.execute(sql)
    aux = mycursor.fetchone()
    print(aux)
    aux1 = str(aux[0])
    status = int(aux1.strip("[").strip("(").strip("'").strip(")").strip("]").strip(",").strip("'"))
    print("status " +str(status))
    if status == 0:
        return False
    else: 
        return True

def qnt_peers_on():
    soma = 0
    print("entrei")
    for a in range(threadCount):
        if verificar_status(a):
            soma = soma + 1
    print("soma de peers"+str(soma))
    return soma

def get_ip_neighbor(id1):
    sql = "SELECT ip FROM peer WHERE id = "+id1+""
    mycursor.execute(sql)
    aux = mycursor.fetchall()
    aux1 = str(aux[0])
    ip1 = aux1.strip("[").strip("(").strip("'").strip(")").strip("]").strip(",").strip("'")
    return ip1
    

def atribuir_vizinhos(id):
    numero_ids = []
    print(threadCount)
    if qnt_peers_on() == 2:
        a = 0
        while a != 1:
            a += 1
            b = random.randint(0,threadCount - 1 )
            if b != id and b not in numero_ids and verificar_status(b):
                numero_ids.append(b)
            else:
                a = a - 1
        return numero_ids
    else:
        print(str(id) + " <-id; threadcount->" + str(threadCount))
        a = 0
        while a != 2:
            a += 1
            b = random.randint(0,threadCount - 1 )
            if b != id and b not in numero_ids and verificar_status(b):
                numero_ids.append(b)
            else:
                a = a - 1
        return numero_ids

def thread_listening(connect, n_t):
    while True:
        data = connect.recv(2048)
        verificar_mensagens[n_t] = 1
        lista_mensagens[n_t] = data
        print(str(lista_mensagens[n_t]) + " numero: "+ str(n_t))


def thread_client(connection,n_thread, listening_port):
    verificar_mensagens[n_thread] = 0
    start_new_thread(thread_listening,(connection, n_thread,))
    while True:
        #interpretar data de modo a ver o que o peer quer fazer, ou conectar ou desconectar
        lock.acquire()
        if verificar_mensagens[n_thread] == 1:
            data = lista_mensagens[n_thread]
            if data[0] == 0:
                aux = True
                set_status_on(n_thread)
                #peers_connected = peers_connected + 1
                if qnt_peers_on() == 1:
                    connection.send(b'-1')
                    aux = False
                print("tpm 0")
                if aux:
                    viz_ids = []
                    viz_ids = atribuir_vizinhos(n_thread)
                    print("vizinhos: "+ str(viz_ids))
                    if viz_ids is None:
                        print("Esperar por mais conexões para iniciar rede overlay vizinhos")
                    else: 
                        if threadCount == 2:
                            #enviar apenas um vizinho, o 2 ip vai com 0.0.0.0 e porta a 0
                            ip1 = get_ip_neighbor(viz_ids[0])
                            packet = send_neighbors(listening_port,1, ip1, '0')
                        else:
                            ip1 = get_ip_neighbor(viz_ids[0])
                            ip2 = get_ip_neighbor(viz_ids[1])
                            packet = send_neighbors(listening_port,N, ip1,ip2)

                #connection.send(send_neighbors("120.20","121.1","122.2",5,4,3))
                    connection.send(packet)
            elif data[0] == 1:
                print("tpm 1")
                connection.send("ole".encode('utf-8'))
            elif data[0] == 10:
                print("recebi um pacote de encaminhamaneto")
            verificar_mensagens[n_thread] = 0
            print("passei aqui")
        lock.release()
         
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
    
    try:
        ServerSocket.bind((host,port))
        
    except socket.error as e:
        print(str(e))
    print('Waiting for Connection')
    ServerSocket.listen(5)

    while True:
        Client, address = ServerSocket.accept()
        add_peer_database(threadCount, address[0], portas_peer, 0)
        
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        verificar_mensagens.append(0)
        lista_mensagens.append('')
        start_new_thread(thread_client,(Client, threadCount,portas_peer,))
        threadCount += 1
        portas_peer +=1
        print('Thread Number: ' + str(threadCount))
    ServerSocket.close()
    