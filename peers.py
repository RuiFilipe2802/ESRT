import socket
import base64

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def connect(ip):
    con = []
    con.append(0)
    con.append(ip)
    print(ip)
    array = base64.b64encode(con)
    
    print(b_con)
    return con
    

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        send = connect(socket.gethostbyname(socket.gethostname()))
        s.connect((HOST, PORT))
        s.sendall(send)
        data = s.recv(1024)
    print('Received', repr(data))