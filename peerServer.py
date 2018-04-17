import json
import time
import socket

HOST, PORT = '127.0.0.1', 23333
bufSize = 1024

def peerServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    peerData = {'account': "xjhuang@s-an.org",
                'passwd': "raspiot",
                'type': "peerServer",
                'nattype':'full cone'}

    s.sendto(json.dumps(peerData).encode(), (HOST, PORT))
    msg, _ = s.recvfrom(bufSize)
    print(msg.decode())

    clientData, _ = s.recvfrom(bufSize)
    clientAddr = tuple(json.loads(clientData.decode())['clientAddr'])
    print(clientAddr)

    time.sleep(2)
    s.sendto('Hi, client'.encode(), clientAddr)
    clientData, _ = s.recvfrom(bufSize)
    print(clientData.decode())


if __name__ == '__main__':
    peerServer()
