import socket
import select
import _thread
import socket
from time import *
import _thread
import numpy as np
from dijkstra import *


ip_source = "10.0.0.3"

ip_neighbours = []      #   IP Neighbours
ipsource = '10.0.0.1'
ipdestino  = '10.0.0.2'
ipsource2 = '10.0.0.1'
ipdestino2 = '10.0.0.3'
routing_table = [['10.0.0.1', '10.0.0.15'], ['10.0.0.2', '10.0.0.2'], ['10.0.0.3', '10.0.0.3']]
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
        msg = input()+'\n'
        print('Input: '+msg)

#set the routing table 
def set_routing_table(packet):
    tamanho = int(packet[1])
    topologia = packet[2:len(packet)]
    array_topologia= [ [ 0 for i in range(3) ] for j in range(tamanho) ]
    counter = 0
    contador = 0
    while(counter < tamanho):
        array_ip1 = topologia[contador:4+contador]
        array_topologia [counter][0] = socket.inet_ntoa(array_ip1)
        array_ip2 = topologia[4+contador:8+contador]
        array_topologia [counter][1] = socket.inet_ntoa(array_ip2)
        array_topologia [counter][2] = int(topologia[8+contador])
        contador +=9
        counter += 1

    return routing_table_calculation(array_topologia,ipsource)


#send normal data
def send_normal_data(packet):
    ip_destino = socket.inet_ntoa(packet[1:5])
    #print(ip_destino)
    ip_rede_destino = []
    if(ip_destino == ip_source):
        print('Chegou ao destino')
    else:
        global routing_table
        x = 0
        while x < len(routing_table):
            if(ip_destino == routing_table[x][0]):
                ip_rede_destino = routing_table[x][1]
                break    
    return ip_rede_destino if len(ip_rede_destino) > 0 else 1


array_topologia = (['10.0.0.1', '10.0.0.2', 2],
                  ['10.0.0.1', '10.0.0.3', 4],
                  ['10.0.0.1', '10.0.0.6', 10],
                  ['10.0.0.2', '10.0.0.3', 3],
                  ['10.0.0.2', '10.0.0.4', 4],
                  ['10.0.0.3', '10.0.0.5', 1],
                  ['10.0.0.4', '10.0.0.5', 5],
                  ['10.0.0.4', '10.0.0.6', 1])

def removePeer(peer):
    global ip_neighbours, ip_source
    topologia = array_topologia
    new_topologia = []
    x = 0
    while x < len(topologia):
        if(topologia[x][0] == peer or topologia[x][1] == peer):
            pass
        else:
            new_topologia.append((topologia[x][0],topologia[x][1],topologia[x][2]))
        x = x + 1
    x  = 0
    if(len(ip_neighbours)==0):
        while x < len(new_topologia):
            if(new_topologia[x][0] not in ip_neighbours  and new_topologia[x][1] not in ip_neighbours):
                if(new_topologia[x][0] == ip_source):
                    ip_neighbours.append(new_topologia[x][1])
                if(new_topologia[x][1] == ip_source):
                    ip_neighbours.append(new_topologia[x][0])
            x = x + 1

    return new_topologia

if __name__ == "__main__":
    
    #_thread.start_new_thread(socket_server,())
    #_thread.start_new_thread(fun_input,())
    print(ip_neighbours)
    print(np.matrix(removePeer("10.0.0.4")))
    print(ip_neighbours)

    