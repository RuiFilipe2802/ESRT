import socket
import random
from _thread import *
import time
import ntplib
from time import ctime, sleep
import threading
import mysql.connector
import struct
from routing.dijkstra import Graph

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9999     # Port to listen on (non-privileged ports are > 1023)

#qnt de vizinhos atribuidos a peer
check_topologia = 0
N = 2
variavel_broadcast = 0
lista_mensagens = []
verificar_mensagens = []
lock = threading.Lock()
N_thread = 0
threadCount = 0
peers_connected = 0

g = Graph()

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
def send_neighbors( n_vizinhos, ip1, ip2):
    send = bytearray(0)
    send.append(10)
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

def set_status_off(id):
    sql = "UPDATE peer set status = 0 WHERE id = "+str(id)
    mycursor.execute(sql)
    mydb.commit()

def verificar_status(b):
    sql = "SELECT status FROM peer WHERE id = "+str(b)+""
    mycursor.execute(sql)
    aux = mycursor.fetchone()
    aux1 = str(aux[0])
    status = int(aux1.strip("[").strip("(").strip("'").strip(")").strip("]").strip(",").strip("'"))
    if status == 0:
        return False
    else: 
        return True

def qnt_peers_on():
    soma = 0
    for a in range(threadCount):
        if verificar_status(a):
            soma = soma + 1
    return soma

def get_ip_neighbor(id1):
    print("get_ip_neigh ->"+str(id1))
    sql = "SELECT ip FROM peer WHERE id = "+str(id1)+""
    mycursor.execute(sql)
    aux = mycursor.fetchall()
    aux1 = str(aux[0])
    ip1 = aux1.strip("[").strip("(").strip("'").strip(")").strip("]").strip(",").strip("'")
    return ip1

def interpretar_trama_custo(b_array):   #tpm, n_viz ; ip dele; ip vizinho; custo
    ip_peer = []
    ip_viz = []
    for a in range(4):
        ip_peer.append(int(b_array[a]))
    for a in range(4):
        ip_viz.append(int(b_array[4+a]))
    print(ip_peer)
    print(ip_viz)
    s_ip_peer = str(ip_peer[0])+"."+str(ip_peer[1])+"."+str(ip_peer[2])+"."+str(ip_peer[3])
    s_ip_viz = str(ip_viz[0])+"."+str(ip_viz[1])+"."+str(ip_viz[2])+"."+str(ip_viz[3])
    print(b_array[8:12])
    inteiro = int.from_bytes(b_array[8:11],'big')
    print(b_array[12:])
    buf = (struct.unpack('>f',b_array[12:]))
    aux = str(buf).strip('(').strip(')').strip(',')
    custo = inteiro + float(str(aux))
    return s_ip_peer, s_ip_viz, custo
    
    
def atribuir_vizinhos(id):
    print("vou atribuir vizinhos id: "+str(id))
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

check_topologia = 0

def thread_listening(connect, n_t):
    while True:
        print("vou ouvir: "+str(n_t))
        data = connect.recv(2048)
        print("liberado ouvi :"+str(n_t))
        verificar_mensagens[n_t] = 1
        lista_mensagens[n_t] = data
        print(str(lista_mensagens[n_t]) + " numero: "+ str(n_t))


def thread_client(connection,n_thread, listening_port):
    verificar_mensagens[n_thread] = 0
    global check_topologia
    global variavel_broadcast
    broadcast_enc = 0
    start_new_thread(thread_listening,(connection, n_thread,))
    while True:
        #interpretar data de modo a ver o que o peer quer fazer, ou conectar ou desconectar
        lock.acquire()
        if verificar_mensagens[n_thread] == 1:
            data = lista_mensagens[n_thread]
            print("sou a data que vais interpretar:"+str(data))
            if data[0] == 0:
                aux = True
                set_status_on(n_thread)
                #peers_connected = peers_connected + 1
                if qnt_peers_on() == 1:
                    connection.send(b'-1')
                    aux = False
                print("tpm 0")
                if aux:
                    g.add_vertex(get_ip_neighbor(n_thread))
                    viz_ids = []
                    viz_ids = atribuir_vizinhos(n_thread)
                    if viz_ids is None:
                        print("Esperar por mais conexões para iniciar rede overlay vizinhos")
                    else: 
                        if qnt_peers_on() == 2:
                            print("tenho 2")
                            #enviar apenas um vizinho, o 2 ip vai com 0.0.0.0 e porta a 0
                            ip1 = get_ip_neighbor(viz_ids[0])
                            packet = send_neighbors(1, ip1, '0')
                        else:
                            ip1 = get_ip_neighbor(viz_ids[0])
                            ip2 = get_ip_neighbor(viz_ids[1])
                            packet = send_neighbors(2, ip1,ip2)
                        connection.send(packet)
                        sleep(0.1)
                #connection.send(send_neighbors("120.20","121.1","122.2",5,4,3))
                    
            elif data[0] == 1:
                print("Desconectou-se")
                # interpretar trama 
                # desbloquear a variavel global para toda a gente enviar
                # atualizar base de dados
                # ver se peer tem vizinhos 
                # remover na topologia peer que saiu
                # remover as ligações 
                connection.send("ole".encode('utf-8'))
                variavel_broadcast = 1
            elif data[0] == 3:
                print("recebi um pacote de encaminhamaneto: "+ str(n_thread)) #interpreto; guardo numa matriz global tpm1;n_viz1;ip4;ip4;custo4
                n_vizinhos = data[1]
                for a in range(n_vizinhos):
                    if a == 0:
                        ip_peer,ip_viz,custo = interpretar_trama_custo(data[2:18])
                        print(ip_peer+", "+ ip_viz+"-> "+str(custo))
                        g.add_edge(ip_peer,ip_viz,custo)
                    if a == 1:
                        print(data[18:30])
                        ip_peer,ip_viz,custo = interpretar_trama_custo(data[18:34])
                        print(ip_peer+", "+ ip_viz+"-> "+str(custo))
                        g.add_edge(ip_peer,ip_viz,custo)
                print("grafo->")
                g.print_graph()
                check_topologia = check_topologia + 1
                broadcast_enc = 1
            print("n topologia:"+str(check_topologia))
            verificar_mensagens[n_thread] = 0
            
            if check_topologia == qnt_peers_on() and broadcast_enc == 1:
                #enviar o grafo
                connection.send("ole".encode('utf-8'))
                print("entrei e agora vou sair"+str(n_thread))
                broadcast_enc = 0
            else:
                connection.send("wait".encode('utf-8'))
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
    