from datetime import date, datetime
import socket
from time import *
import time
import _thread
import ntplib
from datetime import datetime
import os
from dijkstra import *
import struct


PORT_UDP = 5000         # UDP PORT
#   IP ADDRESS
ip_source = "127.0.0.1"
def setTime():
    c = ntplib.NTPClient() 
    response = c.request ('pool.ntp.org') 
    ts = response.tx_time 
    _date = time.strftime ('%y-%m-%d ' , time.localtime(ts)) 
    os.system('sudo date --set='+_date)
    _time = time.strftime('%H:%M:%S', time.localtime(ts))
    t = datetime.fromtimestamp(response.orig_time) 
    os.system('sudo date +%T -s "'+_time+'"')


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


def peerListener(ip_src):
    global neighbours, costsGuardados, enviar, pacote12
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
            print('RECEBI O CUSTO')
            ipReceived = data[1:5]
            ip_rec = socket.inet_ntoa(ipReceived)
            inteiro = int.from_bytes(data[5:9], byteorder='big')
            buf2 = struct.unpack('>f', data[9:])
            aux = str(buf2).strip('(').strip(')').strip(',')
            numero = inteiro + float(str(aux))
            timestamp = datetime.fromtimestamp(numero)
            print(timestamp)

        elif(data[0] == 21):            # DATA
            #UDP para enviar o data com ip = ip_enviar se ip = 1 nao enviar
            print('normal data')


def fun_input():
    while 1:
        global enviar,mensagem
        enviar = input()
        print('Input: '+enviar)
        if(enviar == '6'):
            #socketEnvio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #print('Write message to send:')
            #mensagem = input()
            print('Write ip destination:')
            ip = input()
            #socketEnvio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #socketEnvio.sendto(bytearray(mensagem.encode()),(ip,5000))

            socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            pacote = timeCalc(ip_source)
            socket2.sendto(pacote,(ip,5000))


if __name__ == "__main__":
    
    #   SET MACHINE TIME
    setTime()
    _thread.start_new_thread(fun_input,())
    _thread.start_new_thread(peerListener,())
    while 1:
        pass