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
from testes_do_tiago.dijkstra import *
import select

#   Conf
HOST = '127.0.0.1'      # Standard loopback interface address (localhost)
PORT_TCP = 9999         # TCP PORT
PORT_UDP = 5000         # UDP PORT

#   IP ADDRESS
ip_source = ""

#   Global Variables
neighbours = {}         #   Dictinoary(IP:Cost)
ip_neighbours = []      #   IP Neighbours
routing_table = []      #   Routing Table

enviar = 0 

#   Set time according to NTP Server
def setTime():
    c = ntplib.NTPClient() 
    response = c.request ('pool.ntp.org') 
    ts = response.tx_time 
    _date = time.strftime ('%y-%m-%d ' , time.localtime(ts)) 
    os.system('sudo date --set='+_date)
    _time = time.strftime('%H:%M:%S', time.localtime(ts))
    t = datetime.fromtimestamp(response.orig_time) 
    os.system('sudo date +%T -s "'+_time+'"')
    
#   Connect Peer-Server TYPE 0
def connect(ip):
    now = datetime.now()
    con = bytearray(1)
    con[0] = 0
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    timeStamp = float(now.utcnow().timestamp())
    buf = bytearray(struct.pack('f', timeStamp))
    con.extend(buf)
    return con

#   Disconnect Peer-Server TYPE 1 
def disconnect(ip):
    now = datetime.now()
    dis = bytearray(1)
    dis[0] = 1
    array = ip.split(".")
    for a in range(len(array)):
        dis.append(int(array[a]))
    timeStamp = float(now.utcnow().timestamp())
    buf = bytearray(struct.pack('f', timeStamp))
    dis.extend(buf)
    return dis

#   Error Peer-Server TYPE 2 
def error(ip):
    now = datetime.now()
    err = bytearray(1)
    err[0] = 2
    array = ip.split(".")
    for a in range(len(array)):
        err.append(int(array[a]))
    timeStamp = float(now.utcnow().timestamp())
    buf = bytearray(struct.pack('f', timeStamp))
    err.extend(buf)
    return err

#   Send Costs Peer-Server TYPE 3
def sendCosts(ip):
    send = bytearray(1)
    send[0] = 3
    send.append(len(ip_neighbours))
    x = 0
    while(x < len(ip_neighbours)):
        array = ip.split(".")
        for a in range(len(array)):
            send.append(int(array[a]))              #   IP ORIG
        arrayDest = ip_neighbours[x]
        arrayIpDest = arrayDest.split(".")
        for b in range(len(array)):
            send.append(int(arrayIpDest[b]))        #   IP DEST
        custo = neighbours[ip_neighbours[x]]
        timeStamp = custo
        inteiro = int(timeStamp)
        decimal = timeStamp - inteiro
        b_p = inteiro.to_bytes(4,'big')
        for i in range(len(b_p)):
            send.append(b_p[i])                     #   CUSTO (INT)
        buf = bytearray(struct.pack('>f', decimal))
        for a in range(len(buf)):
            send.append(buf[a])                     #   CUSTO (FLOAT)
        x += 1
    return send

#   Packet with timestamp to calculate latency (Peer-Neighbour) TYPE 20 
def timeCalc(ip):
    now = datetime.now()
    timeStamp = float(now.timestamp())
    inteiro = int(timeStamp)
    decimal = timeStamp - inteiro
    timeCal = bytearray(1)
    timeCal[0] = 20
    array = ip.split(".")
    for b in range(len(array)):
        timeCal.append(int(array[b]))
    b_p = inteiro.to_bytes(4,'big')
    for i in range(len(b_p)):
        timeCal.append(b_p[i])
    buf = bytearray(struct.pack('>f', decimal))
    #timeCal[0] = (0b110)
    for a in range(len(buf)):
        timeCal.append(buf[a])
    return timeCal

#   Neighbours From Server (Server-Peer) TYPE 10
def getNeighbours(res):
    nNeighbours = res[1]
    counter = 0
    contador = 0
    while(counter < nNeighbours):
        array4 = res[2+contador:6+contador]
        if(array4 is not ip_neighbours):
            ip_neighbours.append(socket.inet_ntoa(array4))
            contador += 4
            counter += 1
    return ip_neighbours

#   Send Cost (Neighbour-Peer) TYPE 30
def sendConnectionCost(cost):
    sendCost = bytearray(1)
    sendCost[0] = 30
    array = ip_source.split(".")
    for b in range(len(array)):
        sendCost.append(int(array[b]))
    timeStamp = cost
    inteiro = int(timeStamp)
    decimal = timeStamp - inteiro
    b_p = inteiro.to_bytes(4,'big')
    for i in range(len(b_p)):
        sendCost.append(b_p[i])
    buf = bytearray(struct.pack('>f', decimal))
    for a in range(len(buf)):
        sendCost.append(buf[a])
    return sendCost

#   GET Cost from timestamp
def getTimeStampFromPacket(data):
    inteiro = int.from_bytes(data[5:9],'big')
    timestamp = data[9:]
    buf = struct.unpack('>f', timestamp)
    aux = str(buf).strip('(').strip(')').strip(',')
    numero = inteiro + float(str(aux))
    timestamp = datetime.fromtimestamp(numero)
    return numero

#  SET ROUTING TABLE
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

    return routing_table_calculation(array_topologia,ip_source)

#   SEND NORMAL DATA
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

#   CHECK IF COST CHANGES EVERY 30 SEC
def check_costs():
    while 1:
        sleep(30)
        mudou = 0
        global enviar, neighbours
        cost_stored = dict(neighbours)
        for ip in ip_neighbours:
            socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            pacote = timeCalc(ip_source)
            socket2.sendto(pacote,(ip,5000))
        sleep(5)
        for ip in ip_neighbours:
            if(float(cost_stored[ip]) < float(neighbours[ip])):
                neighbours[ip] = cost_stored[ip]
                mudou = 1
        if(mudou == 1):
            enviar = '4'

#   Thread to communicate with server
def serverComm():
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Waiting for connection')
    try:
        ClientSocket.connect((HOST, PORT_TCP))
    except socket.error as e:
        print(str(e))
    ipOrigin = ClientSocket.getsockname()[0]
    global ip_source
    ip_source = ipOrigin
    print(ip_source)
    _thread.start_new_thread(peerListener,(ip_source,))

    print('Non Blocking - connecting')
    ret = ClientSocket.connect_ex((HOST,PORT_TCP)) #BLOCKING

    if ret != 0:
        print('Non Blocking - failed to connect!')
    
    print('Non Blocking - connected!')
    ClientSocket.setblocking(False)

    inputs = [ClientSocket]
    outputs = [ClientSocket]

    while inputs:
        #print('Non Blocking - waiting...')
        global enviar
        readable,writable,exceptional = select.select(inputs,outputs,inputs,0.5)
        for s in writable:
            #print("Escrever")
            if(enviar == '1'):            # CONNECT
                print('CONNECT')
                packet = connect(ipOrigin)
                ClientSocket.send(packet)
                enviar = 0
            elif(enviar == '2'):          # DISCONNECT 
                print('DISCONNECT')
                packet = disconnect(ipOrigin)
                ClientSocket.send(packet)
                enviar = 0
            elif(enviar == '3'):            # ERROR
                print('ERROR')
                packet = error(ipOrigin)
                ClientSocket.send(packet)
                enviar = 0
            elif(enviar == '4'):            # SEND COSTS FROM NEIGHBOURS
                print('COSTS')
                packet = sendCosts(ipOrigin)
                ClientSocket.send(packet) 
                enviar = 0
        
        for s in readable:
            #print(f'Non Blocking - reading...')
            res = ClientSocket.recv(1024)
            if(res[0] == 10):               # GET NEIGHBOURS
                ip_neighbours = getNeighbours(res)
                for ip in ip_neighbours:
                    socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    pacote = timeCalc(ip_source)
                    socket2.sendto(pacote,(ip,5000))
            elif(res[0] == 11):             # GET TOPOLOGIA
                global routing_table
                routing_table = set_routing_table(res,ip_source)
            elif(res[0] == 12):             # 
                enviar = '4'

        for s in exceptional:
            inputs.remove(s)
            outputs.remove(s)
            break

#   THREAD PEER LISTEN
def peerListener(ip_src):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('.........')
    s.bind((ip_src, PORT_UDP))
    print ("waiting on port:",PORT_UDP)
    while 1:
        data, addr = s.recvfrom(1024)
        if(data[0] == 20):            # RECEIVE TIMESTAMP AND SEND COST
            timestampFromPacket = getTimeStampFromPacket(data)
            tempo1 = datetime.fromtimestamp(timestampFromPacket)
            now = datetime.now()
            timeStamp = float(now.timestamp())
            tempo2 = datetime.fromtimestamp(timeStamp)
            difference = tempo2 - tempo1
            cost = difference.total_seconds()
            socketEnvio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ipDestino = data[1:5]
            ip_dest = socket.inet_ntoa(ipDestino)
            sendCusto = sendConnectionCost(ip_src,cost)
            socketEnvio.sendto(sendCusto,(ip_dest,5000))

        elif(data[0] == 30):           # RECEIVE COST AND STORE 
            ipReceived = data[1:5]
            ip_rec = socket.inet_ntoa(ipReceived)
            inteiro = int.from_bytes(data[5:9], byteorder='big')
            buf2 = struct.unpack('>f', data[9:])
            aux = str(buf2).strip('(').strip(')').strip(',')
            numero = inteiro + float(str(aux))
            timestamp = datetime.fromtimestamp(numero)
            neighbours[ip_rec] = numero
            
def fun_input():
    while 1:
        global enviar
        enviar = input()
        print('Input: '+enviar)

if __name__ == "__main__":
    
    #   SET MACHINE TIME
    setTime()

    #   START THREAD SERVER-PEER TCP
    _thread.start_new_thread(serverComm,())    
    _thread.start_new_thread(fun_input,())

    while 1:
        pass
