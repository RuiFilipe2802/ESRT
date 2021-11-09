import socket
import os
from _thread import *

host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 9998       # Port to listen on (non-privileged ports are > 1023)


def thread_client(connection):
    connection.send(str.encode('Welcome to the Server'))
    while True:
        data = connection.recv(2048)
        reply = 'Server Says: ' + data.decode('utf-8')
        if not data:
            break
        connection.sendall(str.encode(reply))
    connection.close()

if __name__ == "__main__":
    '''with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
                conn.sendall(data)'''
    ServerSocket = socket.socket()
    ThreadCount = 0
    try:
        ServerSocket.bind((host,port))
    except socket.error as e:
        print(str(e))
    print('Waiting for Connection')
    ServerSocket.listen(5)

    while True:
        Client, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        start_new_thread(thread_client,(Client, ))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    ServerSocket.close()
    