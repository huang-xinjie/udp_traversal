import json
import time
import socket

HOST1, PORT, s1p1, s1p2 = '127.0.0.1', 23333, 15002, 12553
HOST2, s2p1 = '192.168.31.16', 6201
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
    dc1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dc2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dc1.sendto("Hi".encode(), (HOST1, s1p1))
    s1Data1, _ = dc1.recvfrom(BUFFSIZE)
    # 同一公网ip, 相同端口, 不同会话   ## 不同 则 对称型
    dc2.sendto("Hi".encode(), (HOST1, s1p1))
    s1Data2, _ = dc2.recvfrom(BUFFSIZE)
    if s1Data1 != s1Data2:
        return 'SymNat'
    # 同一公网ip, 不同端口   ## 不同 则 端口受限锥型
    dc1.sendto("Hi".encode(), (HOST1, s1p2))
    s1Data3, _ = dc1.recvfrom(BUFFSIZE)
    if s1Data1 != s1Data3:
        return 'PRCNat'
    # 不同公网ip          ## 不同 则 受限锥型, 相同 则 全锥型
    dc1.sendto("Hi".encode(), (HOST2, s2p1))
    s1Data4, _ = dc1.recvfrom(BUFFSIZE)
    if s1Data1 != s1Data4:
        return 'RCNat'
    else:
        return 'FCNat'

if __name__ == '__main__':
    peerData = {'account': "ixjhuang@outlook.com",
                'passwd': "raspiot",
                'type': "peerServer",
                'nattype': getNatType()}
    peerServer(peerData)
