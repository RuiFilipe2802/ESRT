import socket
import pickle
import sys

IP_SERVER = "10.0.5.2"
ipO = sys.argv[1]


def cria_pacote(ip, ipO, tipo_p,data,tipo):
    pacote = bytearray(0)
    array = ip.split(".")
    for a in range(len(array)):
        pacote.append(int(array[a]))
    array1 = ipO.split(".")
    for a in range(len(array1)):
        pacote.append(int(array1[a]))
    #print(len(data))
    #if len(data)> 20:
    pacote.append(int(tipo_p))
    if(tipo == 3):
        for i in range(len(data)):
            pacote.append(data[i]) 
    else:
        pacote[9:] = data
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
        print("--------Entrei no enviar connect----------")
        pacote = cria_pacote(IP_SERVER,ipO,1,str(name).encode(),1)
        self.client.send(pacote)
        print("--------Entrei no receber id----------")
        val = self.client.recv(4096)
        print("--------Recebi o id----------")
        print('ID : ' + str(val[5:].decode()))
        return int(val[5:].decode()) # can be int because will be an int id

    def disconnect(self):
        self.client.close()

    def send(self, data, pick=False):
        try:
            if pick:
                print("--------Entrei no enviar pickle----------")
                pacote = cria_pacote(IP_SERVER,ipO,2,pickle.dumps(data),3)
                self.client.sendall(pacote)
            else:
                print("--------Entrei no enviar data----------")
                pacote = cria_pacote(IP_SERVER,ipO,2,str.encode(data),1)
                self.client.sendall(pacote)
                print("--------Entrei no receber data---------")
                replyraw = self.client.recv(4096)
                reply = replyraw[5:]
                print(len(reply))
                #print(reply)
            try:
                reply = pickle.loads(reply)
            except Exception as e:
                print(e)

            return reply
        except socket.error as e:
            print(e)

