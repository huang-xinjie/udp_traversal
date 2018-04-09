import json
import time
import socket

HOST, PORT = '127.0.0.1', 23333
bufSize = 1024

def peerServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    peerData = {'account': "xjhaung@s-an.org",
                'passwd': "raspIot",
                'type': "peerServer"}

    s.sendto(json.dumps(peerData).encode(), (HOST, PORT))
    msg, _ = s.recvfrom(bufSize)
    print(msg.decode())
    clientData, _ = s.recvfrom(bufSize)
    print(clientData)
    clientAddr = clientData.decode()
    print(clientAddr)

    s.sendto('Hi, client'.encode(), clientAddr)
    clientData, _ = s.recvfrom(bufSize)
    print(clientData.decode())
    s.sendto('Hi, client'.encode(), clientAddr)


if __name__ == '__main__':
    peerServer()
