import socket
import base64
import time

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9998       # Port to listen on (non-privileged ports are > 1023)

def connect(ip):
    con = bytearray(1)
    con[0] = 0b0
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    con[2]=time.gmtime(0)
    return con

def disconnect(ip):
    dis = bytearray(1)
    dis[0] = 0b1
    array = ip.split(".")

    for a in range(len(array)):
        dis.append(int(array[a]))
    dis[2]=time.gmtime(0)
    return dis

def error(ip):
    err = bytearray(1)
    err[0] = 0b10
    array = ip.split(".")

    for a in range(len(array)):
        err.append(int(array[a]))
    err[2]=time.gmtime(0)
    return err
    
def send_neighbors(ip,ip1,ip2,porta):
    send=bytearray(1)
    send[0]=0b11
    array = ip.split(".")
    array2 = ip1.split(".")
    array3 = ip2.split(".") 

    for a in range(len(array)):
        send.append(int(array[a]))
    for b in range(len(array2)):
        send.append(int(array2[b]))
    for c in range(len(array3)):
        send.append(int(array3[c]))

    send[4]=time.gmtime(0)
    send[5]=porta

    return send
    
    
def clock_adj(ip):
    c_adj = bytearray(1)
    c_adj[0] = 0b100
    array = ip.split(".")

    for a in range(len(array)):
        c_adj.append(int(array[a]))
    c_adj[2]=time.gmtime(0)
    return c_adj

if __name__ == "__main__":

    ClientSocket = socket.socket()

    print('Waiting for connection')
    try:
        ClientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))

    Response = ClientSocket.recv(1024)
    
    while True:
        Input = input('Say Something: ')
        ClientSocket.send(str.encode(Input))
        Response = ClientSocket.recv(1024)
        print(Response.decode('utf-8'))

    ClientSocket.close()