import json
import time
import socket
import threading

HOST, PORT = '0.0.0.0', 23333
BUFFSIZE = 1024
onlinePeerUser = list()

class PeerUser():
    #{'accountName':{'passwd':passwd,
    #                'serverThread': sthread,
    #                'clientThread': cthread}
    peerUserList = dict()      #map different account
    
    def addUser(self, t):
        if self.authUser(t.account, t.passwd):
            pass
    
    def authUser(self, account, passwd):
        if PeerUser.peerUserList[account]:  # user exists, check passwd
            return PeerUser.peerUserList[account][passwd] == passwd
        else:   # no user exists, add a new user
            return True

class PeerUserThread(threading.Thread):
    """对等的内网主机使用这个"""
    serverAddr = None
    clientAddr = None
    addr = ('',)
    data = None    #data from peerServer or peerClient
    s4s = None     #socket for peerServer
    s4c = None     #socket for peerClient

    def __init__(self, addr, data, s):
        super().__init__()#父类的构造方法
        self.addr = addr
        self.data = json.loads(data.decode())
        self.s4s = s
        self.s4c = s

    def run(self):
        if self.data['type'] == 'peerServer': 
            print("From peerServer, addr is %s" % str(self.addr))
            self.peerServer(self.s4s)
        elif self.data['type'] == 'peerClient':
            print("From peerClient, addr is %s" % str(self.addr))
            self.peerClient(self.s4c)

    def peerServer(self, s4s):
        s4s.sendto("Hello, peerServer, welcome".encode(), self.addr)
        PeerUserThread.serverAddr = json.dumps({'serverAddr': self.addr})
        time.sleep(5)     #确保client已在线
        if PeerUserThread.clientAddr != None:
            s4s.sendto(PeerUserThread.clientAddr.encode(), self.addr)

    def peerClient(self, s4c):
        s4c.sendto("Hello, peerClient, welcome".encode(), self.addr)
        PeerUserThread.clientAddr = json.dumps({'clientAddr': self.addr})
        time.sleep(5)      #确保server已在线
        if PeerUserThread.serverAddr != None:
            s4c.sendto(PeerUserThread.serverAddr.encode(), self.addr)


def checkAccount(data):
    try:
        userData = json.loads(data.decode())
        account = userData['account']
        passwd = userData['passwd']
        if account == 'xjhuang':
            pass
            if passwd == 'raspIot':
                onlinePeerUser.append(account)
        else:
            print('Account or password wrong')
    except Exception:
        print("Error")

def cloudServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))

    thread = list()

    while True:
        data, addr = s.recvfrom(BUFFSIZE)
        thread1 = PeerUserThread(addr, data, s)
        thread1.start()
        thread.append(thread1)

if __name__ == '__main__':
    cloudServer()
