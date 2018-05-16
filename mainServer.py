import json
import time
import socket
import threading

FCNat, ARCNat, PRCNat, SymNat = 'FC Nat', 'ARC Nat', 'PRC Nat', 'Sym Nat'
HOST, PORT, s1p1, s1p2 = '0.0.0.0', 23333, 15002, 12553
HOST2, s2p1 = '139.199.194.49', 16201
BUFFSIZE = 1024

class cloudServer(threading.Thread):
    """对等的内网主机使用这个"""
    account = str()
    peerAddr1 = tuple()
    peerAddr2 = tuple()
    peerType1 = ''
    peerType2 = ''
    s = None

    def __init__(self, account, addr, type, s):
        super().__init__() # 父类的构造方法
        print('From %s peerUser1, addr is %s' % (account, str(addr)))
        self.account = account
        self.peerAddr2 = addr
        self.peerType2 = type
        self.s = s
        threading.Thread(target=self.keepAlive).start()

    def addPeer(self, addr, type):
        print('From %s peerUser2, addr is %s' % (self.account, str(addr)))
        isNewPeer = False if self.peerAddr1 else True
        self.peerAddr1 = self.peerAddr2
        self.peerType1 = self.peerType2
        self.peerAddr2 = addr
        self.peerType2 = type
        if isNewPeer:
            threading.Thread(target=self.travel).start()

    def keepAlive(self):    # until peerUser2 online
        while not self.peerAddr1:
            msgb = '00'.encode()
            self.s.sendto(msgb, self.peerAddr2)
            time.sleep(30)

    def travel(self):
        def buildMsg(plan, addr):
            return (plan + '##' + str(addr)).encode()
        # 其中一个为全锥型
        if self.peerType1 == FCNat:
            # 第一个数 为 方案数，第二个数 为 第几主机
            # msg1 send to low level user
            # msg2 send to high level user
            msg1 = buildMsg("11", self.peerAddr2)
            self.s.sendto(msg1, self.peerAddr1)
            msg1 = buildMsg("12", self.peerAddr1)
            self.s.sendto(msg1, self.peerAddr2)
        elif self.peerType2 == FCNat:
            msg1 = buildMsg("11", self.peerAddr1)
            self.s.sendto(msg1, self.peerAddr2)
            msg2 = buildMsg("12", self.peerAddr2)
            self.s.sendto(msg2, self.peerAddr1)
        # 至少在地址限制型及以上
        elif self.peerType1 == ARCNat:
            msg1 = buildMsg("51", self.peerAddr2)
            self.s.sendto(msg1, self.peerAddr1)
            msg2 = buildMsg("52", self.peerAddr1)
            self.s.sendto(msg1, self.peerAddr2)
        elif self.peerType2 == ARCNat:
            msg1 = buildMsg("51", self.peerAddr1)
            self.s.sendto(msg1, self.peerAddr2)
            msg2 = buildMsg("52", self.peerAddr2)
            self.s.sendto(msg1, self.peerAddr1)
        # 至少在端口限制型及以上
        elif self.peerType1 == PRCNat:
            msg1 = buildMsg("81", self.peerAddr2)
            self.s.sendto(msg1, self.peerAddr1)
            msg2 = buildMsg("82", self.peerAddr1)
            self.s.sendto(msg1, self.peerAddr2)
        elif self.peerType2 == PRCNat:
            msg1 = buildMsg("81", self.peerAddr1)
            self.s.sendto(msg1, self.peerAddr2)
            msg2 = buildMsg("82", self.peerAddr2)
            self.s.sendto(msg1, self.peerAddr1)
        # 均为对称型
        elif self.peerType1 == SymNat and self.peerType2 == SymNat:
            msg1 = buildMsg("rst", self.peerAddr2)
            self.s.sendto(msg1, self.peerAddr1)
            # peerAddr1 will replace with peerAddr2 here
            time.sleep(2)
            msg1 = buildMsg("X1", self.peerAddr1)
            self.s.sendto(msg1, self.peerAddr2)
            msg2 = buildMsg("X2", self.peerAddr2)
            self.s.sendto(msg2, self.peerAddr1)
        
        
        # remove this account
        listenHandler.rmUser(self.account)

  

class listenHandler():
    #{'accountName':{'passwd':passwd,
    #                'cloudThread': cloudThread}
    onlinePeerUserDict = dict()      #map different account
    s = None
    
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))

        listenHandler.onlinePeerUserDict = dict()
        self.run()  #keep running

    def authUser(self, account, passwd):
        if listenHandler.onlinePeerUserDict.get(account):  # user exists, check passwd
            return listenHandler.onlinePeerUserDict[account]['passwd'] == passwd
        # user not exists, add a new user
        return True
    
    def addUser(self, data, addr):
        account, passwd, type = data['account'], data['passwd'], data['nattype']
        if not listenHandler.onlinePeerUserDict.get(account):
            cloudThread = cloudServer(account, addr, type, self.s)
            cloudThread.start()
            userDict = {'passwd':passwd,
                        'cloudThread': cloudThread}
            listenHandler.onlinePeerUserDict[account] = userDict
        else:
            listenHandler.onlinePeerUserDict[account]['cloudThread'].addPeer(addr, type)

    @classmethod
    def rmUser(cls,account):
        if cls.onlinePeerUserDict.get(account):
            del cls.onlinePeerUserDict[account]
            print('%s offline' % account)
            
    def run(self):
        while True:
            try:
                datab, addr = self.s.recvfrom(BUFFSIZE)
                data = json.loads(datab.decode())
                if self.authUser(data['account'], data['passwd']):
                    self.addUser(data, addr)
                else:
                    self.s.sendto("Hello, peerUser. Passwd is not match!".encode(), addr)
                    print('Passwd is not match!')
            except Exception as e:
                print("Server Error: ", str(e))


class detectNatType():    
    def __init__(self):
        # detect server bind 2 ports
        self.ds1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ds2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ds1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ds2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ds1.bind((HOST, s1p1))
        self.ds2.bind((HOST, s1p2))

    def run(self):
        while True:
            try:
                _, addr = self.ds1.recvfrom(BUFFSIZE)
                data = _.decode()
                print('Port1: %s from %s' % (data, str(addr)))
                if data == 'FC detect':
                    self.ds1.sendto(str(addr).encode(), (HOST2, s2p1))
                elif data == 'ARC detect':
                    self.ds2.sendto(str(addr).encode(), addr)
                else:
                    # return client's public address
                    self.ds1.sendto(str(addr).encode(), addr)
            except Exception as e:
                print("Detect Error: ", str(e))

if __name__ == '__main__':
    threading.Thread(target=detectNatType().run).start()
    listenHandler()
