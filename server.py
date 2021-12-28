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
from testes_do_joao import disconnect
import sqlite3
from sqlite3 import Error

host = '10.0.5.3'  # Standard loopback interface address (localhost)
port = 9999     # Port to listen on (non-privileged ports are > 1023)

#qnt de vizinhos atribuidos a peer
check_topologia = 0
N = 2
variavel_broadcast_out = 0
variavel_broadcast_in = 0
lista_mensagens = []
verificar_mensagens = []
lock = threading.Lock()
#numero de thread e define ids de cada thread(peer)
threadCount = 0
#id do que saiu para saber que aquela thread nao precisa de enviar que se desconectou ou conectou
id_broadcast_out = -1
id_broadcast_in = -1
#contar para saber quantos peers entraram na broadcast e fechar metodo qnd todos efetuarem isso
count_for_broadcast_out = 0
count_for_broadcast_in = 0
grafo = []
fui_o_primeiro = -1
mudou_custo = 0
count_for_cust = 0

g = Graph()


mydb = sqlite3.connect('s_database.db',check_same_thread=False)

#pass joao = Johnny1999@

'''mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "johnny1999",
  database = "server_database"
)'''

mycursor = mydb.cursor()

mycursor.execute("DROP TABLE IF EXISTS peer")
mycursor.execute("""CREATE TABLE IF NOT EXISTS peer(
    id integer PRIMARY KEY,
    ip text,
    porta integer,
    status integer
); """)
    

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

    #print(send)
    return send

#tpm 4
def connection_ended(ip):
    c_end = bytearray(1)
    c_end[0] = 13
    array = ip.split(".")

    for a in range(len(array)):
        c_end.append(int(array[a]))
    
    return c_end

#tpm 5
def connection_started(ip):
    con_started = bytearray(1)
    con_started[0] = 12
    array = ip.split(".")
    for a in range(len(array)):
        con_started.append(int(array[a]))
    return con_started

def check_if_peer_is_out_of_neighbor():
    out_neigh = []
    ligacoes = g.get_graph_em_forma_de_array()
    topologia = g.get_vertices()
    for a in topologia:
        if a is not ligacoes:
            out_neigh.append(a)
    return out_neigh


def add_peer_database(id,ip,porta,status):
    try:
        lock.acquire(True)
        mycursor.execute("INSERT INTO peer(id,ip,porta,status) VALUES (?,?,?,?)",(id,ip,porta,status))
        mydb.commit()
    finally:
        lock.release()

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
    s_ip_peer = str(ip_peer[0])+"."+str(ip_peer[1])+"."+str(ip_peer[2])+"."+str(ip_peer[3])
    s_ip_viz = str(ip_viz[0])+"."+str(ip_viz[1])+"."+str(ip_viz[2])+"."+str(ip_viz[3])
    inteiro = int.from_bytes(b_array[8:11],'big')
    buf = (struct.unpack('>f',b_array[12:]))
    aux = str(buf).strip('(').strip(')').strip(',')
    custo = inteiro + float(str(aux))
    return s_ip_peer, s_ip_viz, custo

def trama_grafo(array):
    trama = bytearray(0)
    trama.append(11)
    lenght = len(array)
    trama.append(lenght)
    for i in range(lenght):
        for j in range(3):
            if j == 2:
                inteiro = int(array[i][j])
                decimal = float(array[i][j]) - inteiro
                b_int = inteiro.to_bytes(4,'big')
                trama.extend(b_int)
                buf = struct.pack('>f',decimal)
                trama.extend(buf)
            else:
                ip = array[i][j].split(".")
                #print(ip)
                for a in range(len(ip)):
                    trama.append(int(ip[a]))
    return trama
    
    
def atribuir_vizinhos(id):
    #print("vou atribuir vizinhos id: "+str(id))
    numero_ids = []
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
        #print(str(id) + " <-id; threadcount->" + str(threadCount))
        a = 0
        while a != 2:
            a += 1
            b = random.randint(0,threadCount - 1 )
            #print('LIMITE DE NEIGHBOURS QUE PODE ESGOTAR '+ str(g.lim_of_neighbours(get_ip_neighbor(b))))
            if b != id and b not in numero_ids and verificar_status(b):
                print('LIMITE DE NEIGHBOURS '+ str(g.lim_of_neighbours(get_ip_neighbor(b))))
                numero_ids.append(b)
            else:
                a = a - 1
        return numero_ids


def thread_listening(connect, n_t):
    while True:
        #print("vou ouvir: "+str(n_t))
        data = connect.recv(2048)
        print('DATA : ' + str(data))
        #print('\n')
        #print("liberado ouvi :"+str(n_t))
        verificar_mensagens[n_t] = 1
        lista_mensagens[n_t] = data
        #print(str(lista_mensagens[n_t]) + " numero: "+ str(n_t))


def thread_client(connection,n_thread, listening_port):
    verificar_mensagens[n_thread] = 0

    global check_topologia
    global variavel_broadcast_out
    global variavel_broadcast_in
    global id_broadcast_out
    global count_for_broadcast_out
    global count_for_broadcast_in
    global id_broadcast_in
    global fui_o_primeiro
    global mudou_custo
    global count_for_cust

    broadcast_enc = 0
    broadcast_for_out = 0
    broadcast_for__in = 0
    broadcasr_for_custo = 0
    primeiro = 0

    start_new_thread(thread_listening,(connection, n_thread,))

    while True:
        #interpretar data de modo a ver o que o peer quer fazer, ou conectar ou desconectar
        lock.acquire(True)
        if verificar_mensagens[n_thread] == 1:
            data = lista_mensagens[n_thread]
            #print("sou a data que vais interpretar:" + str(data) + 'nThread: '+str(n_thread))
            if data[0] == 0:
                variavel_broadcast_in = 1
                broadcast_for__in = 1
                broadcast_for_out = 1
                broadcasr_for_custo = 1
                check_topologia = 0
                id_broadcast_in = n_thread
                aux = True
                set_status_on(n_thread)
                if qnt_peers_on() == 1:
                    #print("entrei aqui")
                    connection.send(b'-1')
                    aux = False
                    fui_o_primeiro = 1
                    primeiro = 1
                #print("tpm 0")
                if aux:
                    g.add_vertex(get_ip_neighbor(n_thread))
                    viz_ids = []
                    viz_ids = atribuir_vizinhos(n_thread)
                    if viz_ids is None:
                        print("Esperar por mais conexões para iniciar rede overlay vizinhos")
                    else:
                        if qnt_peers_on() == 2:
                            #print("tenho 2")
                            #enviar apenas um vizinho, o 2 ip vai com 0.0.0.0 e porta a 0
                            ip1 = get_ip_neighbor(viz_ids[0])
                            packet = send_neighbors(1, ip1,'0')
                            fui_o_primeiro = 0
                        else:
                            ip1 = get_ip_neighbor(viz_ids[0])
                            ip2 = get_ip_neighbor(viz_ids[1])
                           
                            packet = send_neighbors(2, ip1,ip2)
                        connection.send(packet)
                        sleep(0.1)
                #connection.send(send_neighbors("120.20","121.1","122.2",5,4,3))
                    
            elif data[0] == 1:  #alguem se desconectou
                print("Desconectou-se")
                set_status_off(n_thread)
                g.remove_peer_lig(get_ip_neighbor(n_thread))
                variavel_broadcast_out = 1
                id_broadcast_out = n_thread
                check_topologia = 0
            
            elif data[0] == 3:  #pacote com custo
                print("recebi um pacote de encaminhamaneto: "+ str(n_thread)) #interpreto; guardo numa matriz global tpm1;n_viz1;ip4;ip4;custo4
                n_vizinhos = data[1]
                for a in range(n_vizinhos):
                    if a == 0:
                        ip_peer,ip_viz,custo = interpretar_trama_custo(data[2:18])
                        #print(ip_peer+", "+ ip_viz+"-> "+str(custo))
                        g.add_edge(ip_peer,ip_viz,custo)
                        fui_o_primeiro = 0
                    if a == 1:
                        #print(data[18:30])
                        ip_peer,ip_viz,custo = interpretar_trama_custo(data[18:34])
                        #print(ip_peer+", "+ ip_viz+"-> "+str(custo))
                        g.add_edge(ip_peer,ip_viz,custo)
                print("grafo ->")
                g.print_graph()

                check_topologia = check_topologia + 1
                broadcast_enc = 1
                #id_broadcast_in = n_thread
            
            elif data[0] == 5:
                #print('MANDA CUSTO = 1')
                mudou_custo = 1
                check_topologia = 0

            print("n topologia:" + str(check_topologia))
            verificar_mensagens[n_thread] = 0
        
        if fui_o_primeiro == 0 and primeiro == 1:
            #print('ENTREI NO IF FUI O PRIMEIRO nthread : %d' % n_thread)
            viz_ids = []
            viz_ids = atribuir_vizinhos(n_thread)
            if qnt_peers_on() == 2:
                #print("tenho 2")
                #enviar apenas um vizinho, o 2 ip vai com 0.0.0.0 e porta a 0
                ip1 = get_ip_neighbor(viz_ids[0])
                packet = send_neighbors(1, ip1,'0')
            else:
                ip1 = get_ip_neighbor(viz_ids[0])
                ip2 = get_ip_neighbor(viz_ids[1])
                packet = send_neighbors(2, ip1,ip2)
            fui_o_primeiro = -1
            primeiro = 0
            connection.send(packet)
            print(packet)
            sleep(0.1)
            
        if check_topologia == qnt_peers_on() and broadcast_enc == 1 and verificar_status(n_thread):
            print('ENTROU A THREAD N: ' + str(n_thread))
            #enviar o grafo
            broadcast_for__in = 1
            broadcast_for_out = 1
            broadcasr_for_custo = 1
            topologia = g.get_graph_em_forma_de_array()
            packet = trama_grafo(topologia)
            print('MANDEI O 11')
            connection.send(packet)
            #print("entrei e agora vou sair"+str(n_thread))
            broadcast_enc = 0
        
        if variavel_broadcast_out == 1 and n_thread != id_broadcast_out and verificar_status(n_thread):
            print("Enviar 13 porque alguem se desconectou esta é a trhea "+str(n_thread)+" desconectou-se a thread"+(str(id_broadcast_out)) + "STATUS NTHREAD :" + str(verificar_status(n_thread)))
            connection.send(connection_ended(get_ip_neighbor(id_broadcast_out)))
            count_for_broadcast_out = count_for_broadcast_out + 1
            if qnt_peers_on() == 1:
                connection.send(b'-1')
                fui_o_primeiro = 1
            else:
                if g.out_of_neighbor(get_ip_neighbor(n_thread)):
                    viz_ids = []
                    viz_ids = atribuir_vizinhos(n_thread)
                    if qnt_peers_on() == 2:
                        #print("tenho 2")
                        #enviar apenas um vizinho, o 2 ip vai com 0.0.0.0 e porta a 0
                        ip1 = get_ip_neighbor(viz_ids[0])
                        packet = send_neighbors(1, ip1,'0')
                    else:
                        ip1 = get_ip_neighbor(viz_ids[0])
                        ip2 = get_ip_neighbor(viz_ids[1])
                        packet = send_neighbors(2, ip1,ip2)
                    connection.send(packet)
            broadcast_for_out = 0

            if count_for_broadcast_out == qnt_peers_on():
                count_for_broadcast_out = 0
                variavel_broadcast_out = 0
                id_broadcast_out = -1

        if variavel_broadcast_in == 1 and n_thread != id_broadcast_in and verificar_status(n_thread):
            #avisar que se conectou
            packet = connection_started(get_ip_neighbor(id_broadcast_in))
            connection.send(packet)
            #sleep(0.1)
            print("Enviar 12 porque alguem se conectou esta é a thread "+str(n_thread)+" conectou-se a thread"+(str(id_broadcast_in)))
            #print(packet)
            count_for_broadcast_in = count_for_broadcast_in + 1
            #print('BROADCAST FOR IN '+str(broadcast_for__in) + 'nTHREAD : '+str(n_thread))
            broadcast_for__in = 0
            #print('COUNT = ' + str(count_for_broadcast_in) + ', QUANT. PEERS ON: ' + str(qnt_peers_on()) + ', BROADCAST FOR IN: '+str(broadcast_for__in))
            if count_for_broadcast_in == qnt_peers_on() - 1:
                #print('SO ENTREI 1 VEZ')
                count_for_broadcast_in = 0
                variavel_broadcast_in = 0
                id_broadcast_in = -1
            
        if mudou_custo == 1 and verificar_status(n_thread):
            print("Enviar 12 porque os custos mudaram esta é a thread "+str(n_thread))
            packet = bytearray(0)
            packet.append(12)
            connection.send(packet)
            count_for_cust += 1
            broadcasr_for_custo = 0
            if count_for_cust == qnt_peers_on():
                count_for_cust = 0
                mudou_custo = 0

        lock.release()
        sleep(0.2)
         
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