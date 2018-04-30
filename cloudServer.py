import json
import time
import socket
import threading

HOST, PORT = '0.0.0.0', 23333
BUFFSIZE = 1024


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
        self.data = data
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
  

class cloudServer():
    #{'accountName':{'passwd':passwd,
    #                'serverThread': sthread,
    #                'clientThread': cthread}
    onlinePeerUserDict = dict()      #map different account
    s = None
    
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))

        self.onlinePeerUserDict = dict()
        self.run()  #keep running

    def authUser(self, account, passwd, userType):
        if self.onlinePeerUserDict.get(account):  # user exists, check passwd
            return self.onlinePeerUserDict[account]['passwd'] == passwd
        # user not exists, add a new user
        return False if userType == 'peerClient' else True

    
    def addUser(self, data, thread):
        userType, account, passwd = data['type'], data['account'], data['passwd']
        if userType == 'peerClient':
            self.onlinePeerUserDict[account]['clientThread'] = thread
        elif userType == 'peerServer':
            userDict = {'passwd':passwd,
                        'serverThread': thread,
                        'clientThread': None}
            self.onlinePeerUserDict[account] = userDict

    def run(self):
        while True:
            datab, addr = self.s.recvfrom(BUFFSIZE)
            data = json.loads(datab.decode())
            if self.authUser(data['account'], data['passwd'], data['type']):
                userThread = PeerUserThread(addr, data, self.s)
                userThread.start()
                self.addUser(data, userThread)
            else:
                self.s.sendto("Hello, peerUser. Passwd not match or peerServer off line!".encode(), addr)
                print('Passwd not match or peerServer offline!')

if __name__ == '__main__':
    cloudServer()
