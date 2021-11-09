import socket
import base64

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9998       # Port to listen on (non-privileged ports are > 1023)

def connect(ip):
    con = bytearray(1)
    con[0] = 0b0
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    return con
    

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