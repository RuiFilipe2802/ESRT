import socket
import base64

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 9998       # Port to listen on (non-privileged ports are > 1023)

def connect(ip):
    con = bytearray(1)
    con[0] = 0b0
    array = ip.split(".")
    for a in range(len(array)):
        con.append(int(array[a]))
    return con
    

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        send = connect(socket.gethostbyname(socket.gethostname()))
        s.connect((HOST, PORT))
        s.sendall(send)
        data = s.recv(1024)
    print('Received', repr(data))