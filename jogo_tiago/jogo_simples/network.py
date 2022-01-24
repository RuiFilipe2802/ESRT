import socket
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

class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "127.0.0.1" # For this to work on your machine this must be equal to the ipv4 address of the machine running the server
                                    # You can find this address by typing ipconfig in CMD and copying the ipv4 address. Again this must be the servers
                                    # ipv4 address. This feild will be the same for all your clients.
        self.port = 5009
        self.addr = (self.host, self.port)

    def connect(self):
        self.id = self.connect(self.addr)
        pacote = cria_pacote(IP_SERVER,ipO,1,str("connectar").encode(),1)
        self.client.connect(pacote)
        id = self.client.recv(2048).decode()
        return id[5:]

    def send(self, data):
        """
        :param data: str
        :return: str
        """
        try:
            print("-----------Enviar Data-----------")
            pacote = cria_pacote(IP_SERVER,ipO,1,str.encode(data),1)
            self.client.send(pacote)
            print("-----------Receber Data-----------")
            replyraw = self.client.recv(2048).decode()
            reply = replyraw[5:]
            return reply
        except socket.error as e:
            return str(e)