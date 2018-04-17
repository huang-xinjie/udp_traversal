import json
import time
import socket

HOST, PORT = '127.0.0.1', 23333
bufSize = 1024

def peerServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    peerData = {'account': "xjhuang@s-an.org",
                'passwd': "raspiot",
                'type': "peerClient",
                'nattype':'full cone'}

    s.sendto(json.dumps(peerData).encode(), (HOST, PORT))
    msg, _ = s.recvfrom(bufSize)
    print(msg.decode())
    serverData, _ = s.recvfrom(bufSize)
    print(serverData)

    serverAddr = tuple(json.loads(serverData.decode())['serverAddr'])
    print(serverAddr)

    time.sleep(2)
    s.sendto('Hi, server'.encode(), serverAddr)
    msg, _ = s.recvfrom(bufSize)
    print(msg.decode())

if __name__ == '__main__':
    peerServer()
