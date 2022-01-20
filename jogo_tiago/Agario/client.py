import socket
import pickle


def cria_pacote(ip,data):
    pacote = bytearray(0)
    array = ip.split(".")
    for a in range(len(array)):
        pacote.append(int(array[a]))
    ip = socket.inet_ntoa(pacote[0:4])
    print(ip)
    pacote[4:] = (bytearray(data.encode()))
    return pacote

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.client.settimeout(10.0)
        self.host = "127.0.0.1"
        self.port = 5009
        self.addr = (self.host, self.port)

    def connect(self, name):
        self.client.connect(self.addr)
        pacote = cria_pacote("10.0.0.3",name)
        self.client.send(pacote)
        val = self.client.recv(12)
        return int(val[5:].decode()) # can be int because will be an int id

    def disconnect(self):
        self.client.close()

    def send(self, data, pick=False):
        try:
            if pick:
                pacote = cria_pacote("10.0.0.3",pickle.dumps(data))
                self.client.sendall(pacote)
            else:
                pacote = cria_pacote("10.0.0.3",data)
                self.client.sendall(str.encode(data))
                reply = self.client.recv(2048*4+5)
            try:
                reply = pickle.loads(reply)
            except Exception as e:
                print(e)

            return reply
        except socket.error as e:
            print(e)



