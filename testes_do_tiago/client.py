import socket
import select
import _thread
from multiprocessing import Process, Lock

msg = []

def socket_server():
    print('Non Blocking - creating socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Non Blocking - connecting')
    ret = s.connect_ex(('localhost',5000)) #BLOCKING

    if ret != 0:
        print('Non Blocking - failed to connect!')
    
    print('Non Blocking - connected!')
    s.setblocking(False)

    inputs = [s]
    outputs = [s]
    while inputs:
        #print('Non Blocking - waiting...')
        readable,writable,exceptional = select.select(inputs,outputs,inputs,0.5)
       
        for s in writable:
            print("Escrever")
            global msg
            if(len(msg)> 0):
                msg = msg.encode()
                byte_array = bytearray(msg)
                print('Non Blocking - sending...')
                data = s.send(byte_array)
                #data = s.send(b'hello\r\n')
                print(f'Non Blocking - sent: {data}')
                outputs.remove(s)
                msg = []
                print(msg)

        for s in readable:
            #print(f'Non Blocking - reading...')
            data = s.recv(1024)
            print(f'Non Blocking - data: {data}')
            #print(f'Non Blocking - closing...')
            #s.close()
            #inputs.remove(s)
            #break

        for s in exceptional:
            #print(f'Non Blocking - error')
            inputs.remove(s)
            outputs.remove(s)
            break
def fun_input():
    while 1:
        global msg
        msg = input()
        print('Input: '+msg)

if __name__ == "__main__":
    
    _thread.start_new_thread(socket_server,())
    _thread.start_new_thread(fun_input(),())
    