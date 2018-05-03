import json
import time
import socket

HOST, PORT = '127.0.0.1', 23333
bufSize = 1024

class peerServer():
    def __init__(self, peerData):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.run()
    
    def contactCloudServer(self):
        # send to cloud server
        self.s.sendto(json.dumps(peerData).encode(), (HOST, PORT))
        msg, _ = self.s.recvfrom(bufSize)
        print(msg.decode())
        if msg.decode() != "Hello, peerClient, welcome":
            raise AssertionError(msg.decode())
    
    def getServerData(self):
        # get server data from cloud
        serverData, _ = self.s.recvfrom(bufSize)
        if _ == (HOST, PORT):
            self.serverAddr = tuple(json.loads(serverData.decode())['serverAddr'])
            return self.serverAddr
        return False
    
    def contactServer(self, msg):
        # waiting for server's msg
        time.sleep(2)
        self.s.sendto(msg.encode(), self.serverAddr)
        msg, _ = self.s.recvfrom(bufSize)
        print(msg.decode())

    def run(self):
        self.contactCloudServer()
        if self.getServerData():
            self.contactServer('Hi, server')

if __name__ == '__main__':
    peerData = {'account': "ixjhuang@outlook.com",
                'passwd': "raspiot",
                'type': "peerClient",
                'nattype':'full cone'}
    peerServer(peerData)
