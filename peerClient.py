import json
import socket

HOST, PORT = '127.0.0.1', 23333
bufSize = 1024

def peerServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    peerData = {'account': "xjhaung@s-an.org",
                'passwd': "raspIot",
                'type': "peerClient"}

    s.sendto(json.dumps(peerData).encode(), (HOST, PORT))
    msg, _ = s.recvfrom(bufSize)
    print(msg.decode())
    serverData, _ = s.recvfrom(bufSize)
    print(serverData)
    serverAddr = serverData.decode()
    print(serverAddr)

    s.sendto('Hi, server'.encode(), serverAddr)

    msg, _ = s.recvfrom(bufSize)
    print(msg.decode())

if __name__ == '__main__':
    peerServer()
