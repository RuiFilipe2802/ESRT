import socket
import base64

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 9998       # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            int_val = []
            for i in range(len(data)):
                int_val.append(int(data[i]))
            print(int_val)
            if not data:
                break
            conn.sendall(data)