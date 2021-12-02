from datetime import datetime
import socket
from time import *
import _thread
import ntplib
from datetime import datetime
import sys
from routing.dijkstra import Graph


from routing.dijkstra import Graph
#import mysql.connector

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9999      # Port to listen on (non-privileged ports are > 1023)
port2 = 5000

ip_source=""
ip_dest1=""
ip_dest2=""
ip_disc=""


            
porta_source=0
porta_dest1=0
porta_dest2=0

'''mydb = mysql.connector.connect(
  host='localhost',
  user="root",
  password="1234",
)

cur = mydb.cursor()

cur.execute("CREATE DATABASE peer_table IF NOT EXIST")
cur.execute("CREATE TABLE routing_table (ip_Dest VARCHAR(255),port VARCHAR(255), prox VARCHAR(255)")
'''

def getTime():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version=3)
    return ctime(int(response.recv_time))
    
#tpm = 0
def connect(ip):
    con = bytearray(0)
    con.append(0)
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    #con.append(getTime())
    #print(con.decode)

    return con

#tpm = 1
def disconnect(ip):
    dis = bytearray(0)
    dis.append(1)
    array = ip.split(".")

    for a in range(len(array)):
        dis.append(int(array[a]))
    #dis.append(getTime())
    return dis

#tpm = 2
def error(ip):
    err = bytearray(1)
    err.append(0b10)
    array = ip.split(".")
    for a in range(len(array)):
        err.append(int(array[a]))
    err.append(getTime())
    return err

def package_interpretation(Response):
    if Response[0] == 3:
        for a in range(len(Response[1:4])):
            ip_source=a.join(".")
        for b in range(len(Response[5:8])):
            ip_dest1=b.join(".")
        for c in range(len(Response[9:12])):
            ip_dest2=c.join(".")
        porta_source=Response[13:14]
        porta_dest1=Response[15:16]
        porta_dest2=Response[17:18]

def sendCosts(ip):
    ip_neighbours = ["127.10.10.1","127.0.0.1"]
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
            send.append(int(arrayIpDest[b]))
        for a in range(8):
            send.append(a)        #   IP DEST
        x += 1
    print(send)
    print(len(send))
    return send


def serverComm():

    ClientSocket = socket.socket()
    print('Waiting for connection')
    try:
        ClientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))
    aux = True
    packet = connect("192.168.58.25")
    print("con")
    print(packet)
    ClientSocket.send(packet)
    Response = ClientSocket.recv(1024)
    print(Response)
    while True:
        if Response == b'-1':
            print("waiting")
            sleep(2)
            packet = connect("192.168.58.25")
            ClientSocket.send(packet)
            Response = ClientSocket.recv(1024)
            print("recebi os neigbhors")
            sleep(1)
            packet = sendCosts("192.168.58.25")
            ClientSocket.send(packet)
            Response = ClientSocket.recv(1024)
        else:
            packet = sendCosts("192.168.58.25")
            print("encam")
            print(packet)
            ClientSocket.send(packet)
            Response = ClientSocket.recv(1024)
            if Response.decode('utf-8') == "wait":
                packet = sendCosts("192.168.58.25")
                print("encam2")
                print(packet)
                ClientSocket.send(packet)
                Response = ClientSocket.recv(1024)
                print(Response.decode('utf-8'))
            
        sleep(5)
            
            
    ClientSocket.close()

g = Graph()

g.add_vertex("127.0.0.1")
g.add_vertex("127.0.0.2")
g.add_vertex("127.0.0.3")
g.add_vertex("127.0.0.4")
g.add_vertex("127.0.0.5")


g.add_edge("127.0.0.1","127.0.0.2", 5)
g.add_edge("127.0.0.2","127.0.0.1",4)
g.add_edge("127.0.0.3","127.0.0.1",6)
g.add_edge("127.0.0.3","127.0.0.2",8)
g.add_edge("127.0.0.4","127.0.0.1",9)
g.add_edge("127.0.0.4","127.0.0.4",12)
g.add_edge("127.0.0.5","127.0.0.3",19)


if __name__ == "__main__":
    print("ola")
    g.print_graph()
    print('ole')
    #g.remove_peer_lig("127.0.0.3")
    print(g.out_of_neighbor("127.0.0.5"))
    #print("separação")
    g.print_graph()

    sleep(20)
    _thread.start_new_thread(serverComm,())
    


    while 1:
        pass