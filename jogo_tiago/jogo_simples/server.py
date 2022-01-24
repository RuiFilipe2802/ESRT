import socket
from _thread import *
import sys


tcp_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_peer.connect(("127.0.0.1", 5009))
ipO = sys.argv[1]

server = 'localhost'
port = 5555

def cria_pacote(ip, ipO, tipo_p,data,tipo):
    pacote = bytearray(0)
    array = ip.split(".")
    for a in range(len(array)):
        pacote.append(int(array[a]))
    array1 = ipO.split(".")
    for a in range(len(array1)):
        pacote.append(int(array1[a]))
    pacote.append(int(tipo_p))
    if(tipo == 3):
        for i in range(len(data)):
            pacote.append(data[i]) 
    else:
        pacote[9:] = data
    return pacote

'''
try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")'''

currentId = "0"
pos = ["0:50,50", "1:100,100"]
def threaded_client(ip):
    global currentId, pos
    pacote_enviar = cria_pacote( ip, ipO,1, str(currentId).encode(),1)
    print("--------Enviar ID----------------")
    tcp_peer.send(str.encode(pacote_enviar))
    currentId = "1"
    reply = ''
    outra = 1
    while True:
        try:
            while outra == 0:
                if ip == ip_recebido and tipo_pacote_recebido == 2:
                    outra = 1
            data = data_recedida
            reply = data.decode('utf-8')
            if not data:
                tcp_peer.send(str.encode("Goodbye"))
                break
            else:
                print("Recieved: " + reply)
                arr = reply.split(":")
                id = int(arr[0])
                pos[id] = reply

                if id == 0: nid = 1
                if id == 1: nid = 0

                reply = pos[nid][:]
                print("Sending: " + reply)
            pacote_envia = cria_pacote(ip,ipO,3,str.encode(reply),3)
            tcp_peer.sendall(pacote_envia)
        except:
            break

    print("Connection Closed")
    tcp_peer.close()

while True:
    #conn, addr = s.accept()
    #print("Connected to: ", addr)
    pacote_jogo_rec = tcp_peer.recv(4096)
    ip_recebido = socket.inet_ntoa(pacote_jogo_rec[:4])
    data_recedida = pacote_jogo_rec[5:]
    print("------------------------------")
    print("IP do Pacote:"+str(ip_recebido))
    print("Tipo do Pacote:"+str(pacote_jogo_rec[4]))

    #start_new_thread(threaded_client, (conn,))
    if(pacote_jogo_rec[4] == 1):
        name = pacote_jogo_rec[5:]
        tipo_pacote_recebido = 1
        start_new_thread(threaded_client, (ip_recebido))
