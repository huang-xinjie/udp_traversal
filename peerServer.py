import json
import time
import socket

HOST1, PORT, s1p1, s1p2 = '127.0.0.1', 23333, 15002, 12553
HOST2, s2p1 = '139.199.194.49', 16201
BUFFSIZE = 1024

class peerServer():
    def __init__(self, peerData):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.run()

    def contactCloudServer(self):
        # send to cloud server
        self.s.sendto(json.dumps(peerData).encode(), (HOST1, PORT))
        msg, _ = self.s.recvfrom(BUFFSIZE)
        print(msg.decode())
        if msg.decode() != "Hello, peerServer, welcome":
            raise AssertionError("Cloud server not working properly!")

    def getClientData(self):
        # get client data from cloud
        clientData, _ = self.s.recvfrom(BUFFSIZE)
        if _ == (HOST1, PORT):
            self.clientAddr = tuple(json.loads(clientData.decode())['clientAddr'])
            return self.clientAddr
        return False
    
    def contactClient(self, msg):
        # waiting for client's msg
        time.sleep(2)
        self.s.sendto(msg.encode(), self.clientAddr)
        clientData, _ = self.s.recvfrom(BUFFSIZE)
        print(clientData.decode())

    def run(self):
        self.contactCloudServer()
        if self.getClientData():
            self.contactClient('Hi, client')

def getNatType():
    Type, ip = '', ''
    dc1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dc1.settimeout(0.5)     # 500ms
    # FC detect
    retry = 0
    while not Type and retry < 3:
        dc1.sendto("FC detect".encode(), (HOST1, s1p1))
        try:
            _, addr = dc1.recvfrom(BUFFSIZE)
            if addr == (HOST2, s2p1):
                Type = 'FC Nat'
                ip = _.decode().split("'")[1]
        except socket.timeout:
            retry += 1   # Not FC Nat
        # ARC detect
    retry = 0
    while not Type and retry < 3:
        dc1.sendto("ARC detect".encode(), (HOST1, s1p1))
        try:
            _, addr = dc1.recvfrom(BUFFSIZE)
            if addr == (HOST1, s1p2):
                Type = 'ARC Nat'
                ip = _.decode().split("'")[1]
        except socket.timeout:
            retry += 1  # Not ARC Nat
    # Sym detect
    retry = 0
    while not Type and retry < 3:
        try:
            dc1.sendto("Sym detect".encode(), (HOST1, s1p1))
            s1Data1, _ = dc1.recvfrom(BUFFSIZE)
            dc1.sendto("Sym detect".encode(), (HOST2, s2p1))
            s2Data1, _ = dc1.recvfrom(BUFFSIZE)
            if s1Data1 != s2Data1:
                Type = 'Sym Nat'
            else:
                Type = 'PRC Nat'
            ip = s1Data1.decode().split("'")[1]
        except socket.timeout:
            if retry >= 2:
                print('Timeout: something error!')
            retry += 1
    return Type

if __name__ == '__main__':
    peerData = {'account': "ixjhuang@outlook.com",
                'passwd': "raspiot",
                'nattype': getNatType()}
    peerServer(peerData)
