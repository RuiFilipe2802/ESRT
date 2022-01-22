import socket
import pickle
import sys

IP_SERVER = "10.0.5.2"
ipO = sys.argv[1]


def cria_pacote(ip, ipO, data, tipo):
    pacote = bytearray(0)
    array = ip.split(".")
    for a in range(len(array)):
        pacote.append(int(array[a]))
    array1 = ipO.split(".")
    for a in range(len(array1)):
        pacote.append(int(array1[a]))
    if tipo == 2:
        for i in range(len(data)):
            pacote.append(data(i)) 
    else: 
        pacote[8:] = data
    return pacote
# FUNCTIONS


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.client.settimeout(10.0)
        self.host = "127.0.0.1"
        self.port = 5009
        self.addr = (self.host, self.port)

    def connect(self, name):
        self.client.connect(self.addr)
        print(ipO)
        pacote = cria_pacote(IP_SERVER,ipO,str(name).encode("utf-8"),1)
        self.client.send(pacote)
        val = self.client.recv(1024)
        print('VAL :' + str(val))
        return int(val[4:].decode()) # can be int because will be an int id

    def disconnect(self):
        self.client.close()

    def send(self, data, pick=False):
        try:
            if pick:
                print('ENTREI ENVIAR PICKLE')
                pacote = cria_pacote(IP_SERVER,ipO,pickle.dumps(data),2)
                self.client.sendall(pacote)
            else:
                pacote = cria_pacote(IP_SERVER,ipO,str.encode(data),1)
                self.client.sendall(pacote)
                replyraw = self.client.recv(2048*4+5)
                print('ENTREI RECEBR PICKLE')
                print(replyraw)
                reply = replyraw[4:]
            try:
                reply = pickle.loads(reply)
            except Exception as e:
                print(e)

            return reply
        except socket.error as e:
            print(e)


