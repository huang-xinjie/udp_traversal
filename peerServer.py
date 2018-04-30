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
        if msg.decode() != "Hello, peerServer, welcome":
            raise AssertionError("Cloud server not working properly!")

    def getClientData(self):
        # get client data from cloud
        clientData, _ = self.s.recvfrom(bufSize)
        self.clientAddr = tuple(json.loads(clientData.decode())['clientAddr'])
        print(self.clientAddr)
    
    def contactClient(self, msg):
        # waiting for client's msg
        time.sleep(2)
        self.s.sendto(msg.encode(), self.clientAddr)
        clientData, _ = self.s.recvfrom(bufSize)
        print(clientData.decode())

    def run(self):
        self.contactCloudServer()
        while True:
            self.getClientData()
            self.contactClient('Hi, client')

if __name__ == '__main__':
    peerData = {'account': "ixjhuang@outlook.com",
                'passwd': "raspiot",
                'type': "peerServer",
                'nattype':'full cone'}
    peerServer(peerData)
