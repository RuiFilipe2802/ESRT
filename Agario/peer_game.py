from datetime import date, datetime
import socket
from time import *
import time
import _thread
import ntplib
from datetime import datetime
import threading
import sys
import os
import struct
from testes_do_tiago.dijkstra import *
import select
import numpy as np
from _thread import *
import pickle
import random
import math

#   Conf
HOST = '10.0.5.3'      # Standard loopback interface address (localhost)
PORT_TCP = 9999         # TCP PORT
PORT_UDP = 5000         # UDP PORT

lock = threading.Lock()

#   IP ADDRESS
ip_source = ""

#   Global Variables
neighbours = {}         #   Dictinoary(IP:Cost)
ip_neighbours = []      #   IP Neighbours
routing_table = []      #   Routing Table
array_topologia = []

mensagem = ""

enviar = 0 
disconnect_var = 0
costsGuardados = -1
pacote12 = 0

arrayCustos = []

#   Set time according to NTP Server
def setTime():
    c = ntplib.NTPClient() 
    response = c.request ('pool.ntp.org') 
    ts = response.tx_time 
    _date = time.strftime ('%y-%m-%d ' , time.localtime(ts)) 
    os.system('date --set='+_date)
    _time = time.strftime('%H:%M:%S', time.localtime(ts))
    t = datetime.fromtimestamp(response.orig_time) 
    os.system('date +%T -s "'+_time+'"')
    
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
    global ip_neighbours
    nNeighbours = res[1]
    #print('NUMERO DE NEIGHBOURS ----------------------> %d' % nNeighbours)
    counter = 0
    contador = 0
    while(counter < nNeighbours):
        array4 = res[2+contador:6+contador]
        ip = socket.inet_ntoa(array4)
        if(ip not in ip_neighbours):
            ip_neighbours.append(ip)
            contador += 4
            counter += 1
    return ip_neighbours

#   Send Cost (Neighbour-Peer) TYPE 30
def sendConnectionCost(cost):
    #print(ip_source)
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
    #print('ENTREI NO ROUTING TABLE')
    tamanho = int(packet[1])
    global array_topologia
    topologia = packet[2:len(packet)]
    array_topologia= [[ 0 for i in range(3) ] for j in range(tamanho)]
    counter = 0
    contador = 0
    while(counter < tamanho):
        array_ip1 = topologia[contador:4+contador]
        array_topologia [counter][0] = socket.inet_ntoa(array_ip1)
        array_ip2 = topologia[4+contador:8+contador]
        array_topologia [counter][1] = socket.inet_ntoa(array_ip2)
        inteiro = topologia[8+contador:12+contador]
        decimal = topologia[12+contador:16+contador]
        inteiro2 = int.from_bytes(inteiro,'big')
        decimal2 = decimal
        buf = struct.unpack('>f', decimal2)
        aux = str(buf).strip('(').strip(')').strip(',')
        numero = inteiro2 + float(str(aux))
        #print(numero)
        #print(inteiro)
        array_topologia [counter][2] = float(numero)
        contador += 16
        counter += 1

    return routing_table_calculation(array_topologia,ip_source)

#   NEXT DATA HOP
def next_data_hop(packet):
    ip_destino = socket.inet_ntoa(packet[1:5])
    #print('IP DESTINO :' + str(ip_destino))
    ip_rede_destino = ""
    if(ip_destino == ip_source):
        print('Chegou ao destino')
        print(packet[5:len(packet)])
    else:
        global routing_table
        x = 0
        #print(np.matrix(routing_table))
        while x < len(routing_table):
            if(ip_destino == routing_table[x][0]):
                ip_rede_destino = routing_table[x][1]
                #print('IP REDE DESTINO :' + str(ip_rede_destino))
                break
            x += 1
    return ip_rede_destino if len(ip_rede_destino) > 0 else 1

#   CHECK IF COST CHANGES EVERY 30 SEC
def check_costs():
    global disconnect_var
    global enviar, neighbours
    while len(ip_neighbours) == 0:
        pass
    while disconnect_var == 0:
        sleep(15)
        #print('ENTREI')
        mudou = 0
        #print(neighbours)
        cost_stored = dict(neighbours)
        for ip in ip_neighbours:
                    socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    pacote = timeCalc(ip_source)
                    socket2.sendto(pacote,(ip,5000))
        sleep(0.2)
        for ip in ip_neighbours:
            #print('VALORES:')
            new = float(neighbours[ip])
            #print(cost_stored[ip])
            if not cost_stored:
                old = 100 
                cost_stored[ip] = 100            
            else:
                old = float(cost_stored[ip])
            #print(x<y)
            if(2 * new < old):
                print('MUDA PARA MELHOR')
                #neighbours[ip] = cost_stored[ip]
                mudou = 1
            if(new > 5 * old):
                print('MUDA PARA PIOR')
                mudou = 1
                
        if(mudou == 1):
            enviar = '5'

#   SEND DATA
def sendData(msg,ip_to,ip_from,tpm):
    #print('AQUI')
    #print(msg)
    #print(ip)
    pacote1 = bytearray(1)
    pacote1[0] = 21
    array = ip_to.split(".")
    for a in range(len(array)):
        pacote1.append(int(array[a]))
    array1 = ip_from.split(".")
    for b in range(len(array1)):
        pacote1.append(int(array[b]))
    pacote1.append(tpm)
    pacote1[6:] = (bytearray(msg.encode()))
    #print('PACOTE:')
    #print(pacote)
    socketEnvio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketEnvio.sendto(pacote1,(ip_to,5000))


def removePeer(peer):
    global ip_neighbours, ip_source, array_topologia
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
    print('\n\nTOPOLOGIA')
    print(new_topologia)
    if(len(ip_neighbours)==0):
        while x < len(new_topologia):
            print(str(new_topologia[x][0]) + str(new_topologia[x][1]))

            if(new_topologia[x][0] not in ip_neighbours  and new_topologia[x][1] not in ip_neighbours):
                if(new_topologia[x][0] == ip_source):
                    ip_neighbours.append(new_topologia[x][1])
                if(new_topologia[x][1] == ip_source):
                    ip_neighbours.append(new_topologia[x][0])
            x = x + 1

    array_topologia = new_topologia
    return new_topologia

#   Thread to communicate with server
def serverComm():
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Waiting for connection')
    try:
        ClientSocket.connect((HOST, PORT_TCP))
    except socket.error as e:
        print(str(e))
    ipOrigin = ClientSocket.getsockname()[0]
    global ip_source, ip_neighbours, pacote12, costsGuardados
    global neighbours
    ip_source = ipOrigin
    print(ip_source)
    _thread.start_new_thread(peerListener,(ip_source,))
    _thread.start_new_thread(check_costs,())

    #print('Non Blocking - connected!')
    ClientSocket.setblocking(False)

    inputs = [ClientSocket]
    outputs = [ClientSocket]

    while inputs:
        lock.acquire(True)
        #print('Non Blocking - waiting...')
        global enviar, disconnect_var
        global routing_table
        readable,writable,exceptional = select.select(inputs,outputs,inputs,0.5)
        for s in writable:
            #print("Escrever")
            if(enviar == '1'):             # CONNECT
                print('CONNECT')
                packet = connect(ipOrigin)
                ClientSocket.send(packet)
                enviar = 0
                disconnect_var = 0
            elif(enviar == '2'):           # DISCONNECT 
                print('DISCONNECT')
                packet = disconnect(ipOrigin)
                neighbours.clear()
                ip_neighbours.clear()
                print('IP NEIGHBOURS :' + str(ip_neighbours))
                print('NEIGHBOURS :' + str(neighbours))
                ClientSocket.send(packet)
                #outputs.remove(ClientSocket)
                enviar = 0
                disconnect_var = 1
            elif(enviar == '3'):            # ERROR
                print('ERROR')
                packet = error(ipOrigin)
                ClientSocket.send(packet)
                enviar = 0
            elif(enviar == '4'):            # SEND COSTS FROM NEIGHBOURS
                print('SEND COSTS')
                packet = sendCosts(ipOrigin)
                ClientSocket.send(packet) 
                enviar = 0
            elif(enviar == '5'):            # COSTS CHANGED
                print('NEW COSTS')
                packet = bytearray(1)
                packet[0] = 5
                array = ip_source.split(".")
                for a in range(len(array)):
                    packet.append(int(array[a]))
                ClientSocket.send(packet)
                enviar = 0
        
        for s in readable:
            #print(f'Non Blocking - reading...')
            res = ClientSocket.recv(1024)
            print(res)
            if(res[0] == 10):               # GET NEIGHBOURS
                print('RECEBI VIZINHOS')
                ip_neighbours = getNeighbours(res)
                pacote12 = 1
                #print(pacote12)
                for ip in ip_neighbours:
                    socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    pacote = timeCalc(ip_source)
                    socket2.sendto(pacote,(ip,5000))
                
            elif(res[0] == 11):             # GET TOPOLOGIA
                routing_table = set_routing_table(res)
                print('NEIGHBOURS :')
                print(neighbours)
                print('ROUTING TABLE :')
                print(np.matrix(routing_table))

            elif(res[0] == 12):             # ask costs
                print('ENTREI NO 12')
                costsGuardados = 0
                pacote12 = 1
                for ip in ip_neighbours:
                    socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    pacote = timeCalc(ip_source)
                    socket2.sendto(pacote,(ip,5000))

            elif(res[0] == 13):             # remover ip dos neighbours se tiver
                #print('13')
                array = res[1:5]
                #print('ENTREI AQUI')
                ip = socket.inet_ntoa(array)
                if ip in ip_neighbours: ip_neighbours.remove(ip)
                if ip in neighbours.keys():
                    neighbours.pop(ip)
                print('NEIGHBOURS DEPOIS: ' + str(ip_neighbours))
                print('DICIONARIO DEPOIS: ' + str(neighbours))
                nova_topologia = removePeer(ip)
                print('NOVA TOPOLOGIA:')
                routing_table = routing_table_calculation(nova_topologia,ip_source)
                print(np.matrix(routing_table))

        for s in exceptional:
            inputs.remove(s)
            outputs.remove(s)
            break
        lock.release()
        sleep(0.1)

#   THREAD PEER LISTEN
def peerListener(ip_src):
    global neighbours, costsGuardados, enviar, pacote12,recebido
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('.........')
    s.bind((ip_src, PORT_UDP))
    print ("waiting on port:",PORT_UDP)
    while 1:
        data, addr = s.recvfrom(1024)
        if(data[0] == 20):            # RECEIVE TIMESTAMP AND SEND COST
            #print('RECEBI O TIMESTAMP')
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
            sendCusto = sendConnectionCost(cost)
            socketEnvio.sendto(sendCusto,(ip_dest,5000))

        elif(data[0] == 30):           # RECEIVE COST AND STORE 
            #print('RECEBI O CUSTO')
            ipReceived = data[1:5]
            ip_rec = socket.inet_ntoa(ipReceived)
            inteiro = int.from_bytes(data[5:9], byteorder='big')
            buf2 = struct.unpack('>f', data[9:])
            aux = str(buf2).strip('(').strip(')').strip(',')
            numero = inteiro + float(str(aux))
            f = open("logs2.txt", "a")
            f.write(str(numero) + '\n')
            f.close()
            arrayCustos.append(numero)
            if len(arrayCustos) == 10:
                mean = np.mean(arrayCustos)
                print('Media :' + str(mean))
            timestamp = datetime.fromtimestamp(numero)
            if(ip_rec in ip_neighbours):
                neighbours[ip_rec] = numero
            if (costsGuardados == -1):
                costsGuardados = 0
            lock.acquire(True)
            costsGuardados += 1
            lock.release()
            #print('-----------------')
            #print('COSTS GUARDADOS : '+str(costsGuardados) + '\nlen Neig : ' + str(len(ip_neighbours)) + '\npacote12 : ' + str(pacote12))
            if (costsGuardados == len(ip_neighbours) and pacote12 == 1):
                #print('ENTREI NOS COSTS GUARDADOS')
                enviar = '4' 
                costsGuardados = 0
                pacote12 = 0

        elif(data[0] == 21):            # DATA
            ip_enviar = next_data_hop(data)
            if(ip_enviar != 1):
                socketEnvio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                socketEnvio.sendto(data,(ip_enviar,5000))
            else:
                #recebi data do jogo
                global data_game
                recebido = 1
                data_game = data
            #UDP para enviar o data com ip = ip_enviar se ip = 1 nao enviar
            print('normal data')


recebido = 0
data_game = ""

PORT = 5552

BALL_RADIUS = 5
START_RADIUS = 7

ROUND_TIME = 60 * 5

MASS_LOSS_TIME = 7

W, H = 1000, 500

# dynamic variables
players = {}
balls = []
connections = 0
_id = 0
colors = [(255,0,0), (255, 128, 0), (255,255,0), (128,255,0),(0,255,0),(0,255,128),(0,255,255),(0, 128, 255), (0,0,255), (0,0,255), (128,0,255),(255,0,255), (255,0,128),(128,128,128), (0,0,0)]
start = False
stat_time = 0
game_time = "Starting Soon"
nxt = 1


# FUNCTIONS
def release_mass(players):
	for player in players:
		p = players[player]
		if p["score"] > 8:
			p["score"] = math.floor(p["score"]*0.95)


def check_collision(players, balls):
	to_delete = []
	for player in players:
		p = players[player]
		x = p["x"]
		y = p["y"]
		for ball in balls:
			bx = ball[0]
			by = ball[1]

			dis = math.sqrt((x - bx)**2 + (y-by)**2)
			if dis <= START_RADIUS + p["score"]:
				p["score"] = p["score"] + 0.5
				balls.remove(ball)


def player_collision(players):
	sort_players = sorted(players, key=lambda x: players[x]["score"])
	for x, player1 in enumerate(sort_players):
		for player2 in sort_players[x+1:]:
			p1x = players[player1]["x"]
			p1y = players[player1]["y"]

			p2x = players[player2]["x"]
			p2y = players[player2]["y"]

			dis = math.sqrt((p1x - p2x)**2 + (p1y-p2y)**2)
			if dis < players[player2]["score"] - players[player1]["score"]*0.85:
				players[player2]["score"] = math.sqrt(players[player2]["score"]**2 + players[player1]["score"]**2) # adding areas instead of radii
				players[player1]["score"] = 0
				players[player1]["x"], players[player1]["y"] = get_start_location(players)
				print(f"[GAME] " + players[player2]["name"] + " ATE " + players[player1]["name"])


def create_balls(balls, n):
	for i in range(n):
		while True:
			stop = True
			x = random.randrange(0,W)
			y = random.randrange(0,H)
			for player in players:
				p = players[player]
				dis = math.sqrt((x - p["x"])**2 + (y-p["y"])**2)
				if dis <= START_RADIUS + p["score"]:
					stop = False
			if stop:
				break

		balls.append((x,y, random.choice(colors)))


def get_start_location(players):
	while True:
		stop = True
		x = random.randrange(0,W)
		y = random.randrange(0,H)
		for player in players:
			p = players[player]
			dis = math.sqrt((x - p["x"])**2 + (y-p["y"])**2)
			if dis <= START_RADIUS + p["score"]:
				stop = False
				break
		if stop:
			break
	return (x,y)

client_list = []
client_dict = {}
mensagem = []

def thread_client(id,ip):
    global client_list, data_game
    global connections, players, balls, game_time, nxt, start
    current_id = id

    while(client_list[current_id] == 0):
        pass
    pacote = mensagem[current_id]
    name = pacote[10:].decode("utf-8")
    print("[LOG]", name, "connected to the server.")
    color = colors[current_id]
    x, y = get_start_location(players)
    players[current_id] = {"x":x, "y":y,"color":color,"score":0,"name":name}  # x, y color, score, name

    #falta aqui qql coisa
    while True:
        if start:
            game_time = round(time.time()-start_time)
            # if the game time passes the round time the game will stop
            if game_time >= ROUND_TIME:
                start = False
            else:
                if game_time // MASS_LOSS_TIME == nxt:
                    nxt += 1
                    release_mass(players)
                    print(f"[GAME] {name}'s Mass depleting")
        
        while client_list[current_id] == 0:
            pass
        pacote = mensagem[current_id]

        if not pacote:
            break

        pacote = pacote.decode("utf-8")

        # look for specific commands from recieved data
        if pacote.split(" ")[0] == "move":
            split_data = pacote.split(" ")
            x = int(split_data[1])
            y = int(split_data[2])
            players[current_id]["x"] = x
            players[current_id]["y"] = y

            # only check for collison if the game has started
            if start:
                check_collision(players, balls)
                player_collision(players)

            # if the amount of balls is less than 150 create more
            if len(balls) < 150:
                create_balls(balls, random.randrange(100,150))
                print("[GAME] Generating more orbs")

            send_data = pickle.dumps((balls,players, game_time))

        elif pacote.split(" ")[0] == "id":
            send_data = str.encode(str(current_id))  # if user requests id then send it

        elif pacote.split(" ")[0] == "jump":
            send_data = pickle.dumps((balls,players, game_time))
        else:
            # any other command just send back list of players
            send_data = pickle.dumps((balls,players, game_time))

        # send data back to clients
        #conn.send(send_data)
        sendData(send_data,ip,ip_source,3)
        #  # if an exception has been reached disconnect client
    time.sleep(0.001)



def int_ip(data):
    ip = str(data[0])+"."+str(data[1])+"."+str(data[2])+"."+str(data[3])
    return ip

def gaming():
    global connections, players, balls, game_time, nxt, start, start_time, _id
    create_balls(balls, random.randrange(200,250))

    print("[GAME] Setting up level")
    print("[SERVER] Waiting for connections")
    while True:
        while recebido == 0:
            pass
        if data_game[9] == 1:
            connections += 1
            ip = int_ip(data_game[5:8])
            _thread.start_new_thread(gaming,(_id,ip))
            client_list.append(0)
            client_dict[ip] = _id
            mensagem.append("")
            _id += 1
        elif data_game[9] == 2:
            print("desconexao")
        elif data_game[9] == 3:
            ip = int_ip(data_game[5:8])
            a = client_dict[ip]
            client_list[a] = 1
            mensagem[a] = data_game[10:]
            print("data recebida")
        if connections >=1 and not(start):
            start = True
            start_time = time.time()
            print("[STARTED] Game started")
            #comparar ip e ver posiçao da lista e desbloquear essa     

            

if __name__ == "__main__":
    
    #   SET MACHINE TIME
    setTime()

    #   START THREAD SERVER-PEER TCP
    _thread.start_new_thread(serverComm,())    
    _thread.start_new_thread(gaming,())

    while 1:
        pass