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

ip_neighbours = ["10.0.0.1","10.0.0.2"]

def timeCalc(ip):
    now = datetime.now()
    timeStamp = float(now.timestamp())
    inteiro = int(timeStamp)
    decimal = timeStamp - inteiro
    timeCal = bytearray(1)
    timeCal[0] = 10
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

def sendCosts(ip):
    send = bytearray(1)
    send[0] = 3
    send.append(len(ip_neighbours))
    x = 0
    while(x < len(ip_neighbours)):
        array = ip.split(".")
        for a in range(len(array)):
            send.append(int(array[a]))
        arrayDest = ip_neighbours[x]
        arrayIpDest = arrayDest.split(".")
        for b in range(len(array)):
            send.append(int(arrayIpDest[b]))
        x += 1
    return send

def getTimeStampFromPacket(data):
    inteiro = int.from_bytes(data[5:9],'big')
    timestamp = data[9:]
    buf = struct.unpack('>f', timestamp)
    aux = str(buf).strip('(').strip(')').strip(',')
    numero = inteiro + float(str(aux))
    timestamp = datetime.fromtimestamp(numero)
    return numero


if __name__ == "__main__":
    
    '''packet = timeCalc('10.0.0.1')
    inteiro = int.from_bytes(packet[5:9],'big')
    timestamp = packet[9:]
    buf = struct.unpack('>f', timestamp)
    aux = str(buf).strip('(').strip(')').strip(',')
    numero = inteiro + float(str(aux))
    timestamp= datetime.fromtimestamp(numero)
    print(timestamp)'''
    ip_src = '10.0.0.1'

    boas = timeCalc(ip_src)
    time = getTimeStampFromPacket(boas)
    tempo1 = datetime.fromtimestamp(time)
    sleep(2)
    now = datetime.now()
    timeStamp = float(now.timestamp())
    tempo2 = datetime.fromtimestamp(timeStamp)
    difference = tempo2 - tempo1
    cost = difference.total_seconds()
    #socketEnvio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ipDestino = boas[1:5]
    ip_dest = socket.inet_ntoa(ipDestino)
    sendCost = bytearray(1)
    sendCost[0] = 30
    array = ip_src.split(".")
    for b in range(len(array)):
        sendCost.append(int(array[b]))
    timeStamp = cost
    inteiro = int(timeStamp)
    decimal = timeStamp - inteiro
    b_p = inteiro.to_bytes(4,'big')
    for i in range(len(b_p)):
        sendCost.append(b_p[i])
    buf = bytearray(struct.pack('>f', decimal))
    #timeCal[0] = (0b110)
    for a in range(len(buf)):
        sendCost.append(buf[a])
    
    z = 0
    for x in range(len(sendCost)):
        print(sendCost[z])
        z += 1

    buf2 = struct.unpack('>f', buf)
    aux = str(buf2).strip('(').strip(')').strip(',')
    numero = inteiro + float(str(aux))
    timestamp = datetime.fromtimestamp(numero)
    print(numero)

    for ip in ip_neighbours:
                print(ip)

    while(1):            
        pass
