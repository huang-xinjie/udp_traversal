import json
import time
import socket
import threading

FCNat, ARCNat, PRCNat, SymNat = 'FC Nat', 'ARC Nat', 'PRC Nat', 'Sym Nat'
HOST1, PORT, s1p1, s1p2 = '123.207.161.147', 23333, 15002, 12553
HOST2, s2p1 = '139.199.194.49', 16201
BUFFSIZE = 1024

class peerUser():
    selfData = None
    def __init__(self, selfData):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # send to cloud server
        self.selfData = selfData
        self.s.sendto(json.dumps(selfData).encode(), (HOST1, PORT))
        msg = self.__keepAlive()
        peerAddr = self.travel(msg)
        if peerAddr:
            self.p2p(peerAddr)

    def p2p(self, peerAddr):
        def recvFromPeerUser():
            while True:
                msgb, _ = self.s.recvfrom(BUFFSIZE)
                print('\r   From peerUser: ', msgb.decode())
                print('\nSend to peerUser: ', end='')
                if msgb == 'q'.encode():
                    print('OK, connection is closed.')
                    break
        def sendToPeerUser():
            while True:
                msg = input('Send to peerUser: ')
                self.s.sendto(msg.encode(), peerAddr)
                if msg == 'q':
                    print('OK, connection is closed.')
                    break
        threading.Thread(target=recvFromPeerUser).start()
        threading.Thread(target=sendToPeerUser).start()

    def travel(self, msg):
        plan, peerAddrData = msg.split('##')
        _, peerIP, peerPort = peerAddrData.split("'")
        peerAddr = (peerIP, int(peerPort[2:-1]))
        # Full Cone & other
        if plan == '11':
            msgb, peerAddr = self.s.recvfrom(BUFFSIZE)
            if msgb.decode() == '12':
                print('Get %s from peer: %s' % (msgb.decode(), str(peerAddr)))
                self.s.sendto('Hello, peer.'.encode(), peerAddr)
        # Other & Full Cone
        elif plan == '12':
            time.sleep(3)   # waitting peerUser for ready
            self.s.sendto('12'.encode(), peerAddr)
            msgb, peerAddr = self.s.recvfrom(BUFFSIZE)
            print(msgb.decode())
        # Address Restricted Cone & higher level
        elif plan == '51':
            self.s.sendto('51'.encode(), peerAddr)  # hole punch
            msgb, peerAddr = self.s.recvfrom(BUFFSIZE)
            if msgb.decode() == '52':
                print('Get %s from peer: %s' % (msgb.decode(), str(peerAddr)))
                self.s.sendto('Hello, peer.'.encode(), peerAddr)
        # Higher level & Address Restricted Cone
        elif plan == '52':
            time.sleep(3)   # waitting peerUser to hole punch
            self.s.sendto('52'.encode(), peerAddr)
            msgb, peerAddr = self.s.recvfrom(BUFFSIZE)
            print(msgb.decode())
        # Port Restricted Cone & higher level
        elif plan == '81':
            peerIP, peerPort = list(peerAddr)
            for i in range(10): # hole punch
                self.s.sendto('81'.encode(), (peerIP, peerPort+i))
                time.sleep(0.1)
            msgb, peerAddr = self.s.recvfrom(BUFFSIZE)
            if msgb.decode() == '82':
                print('Get %s from peer: %s' % (msgb.decode(), str(peerAddr)))
                self.s.sendto('Hello, peer.'.encode(), peerAddr)
        # Higher level & Port Restricted Cone
        elif plan == '82':
            time.sleep(5)   # waitting peerUser to hole punch
            self.s.sendto('82'.encode(), peerAddr)
            msgb, peerAddr = self.s.recvfrom(BUFFSIZE)
            print(msgb.decode())
        # Symmetric & Symmetric
        elif plan == 'X1':
            peerIP, peerPort = list(peerAddr)
            for i in range(10): # hole punch
                print('Port: ', peerPort+i)
                self.s.sendto('X1'.encode(), (peerIP, peerPort+i))
            msgb, peerAddr = self.s.recvfrom(BUFFSIZE)
            print(msgb)
            if msgb.decode() == 'X2':
                print('Get %s from peer: %s' % (msgb.decode(), str(peerAddr)))
                self.s.sendto('Hello, peer.'.encode(), peerAddr)
        elif plan == 'X2': 
            time.sleep(1)
            peerIP, peerPort = list(peerAddr)
            for i in range(10): # hole punch
                print('Port: ', peerPort+i)
                self.s.sendto('X2'.encode(), (peerIP, peerPort+i))
            msgb, peerAddr = self.s.recvfrom(BUFFSIZE)
            print(msgb.decode())
        elif plan == 'rst':
            self.__init__(self.selfData)
            return None
        return peerAddr
    
    def __keepAlive(self):
        while True:
            msgb, _ = self.s.recvfrom(BUFFSIZE)
            if _ == (HOST1, PORT):
                msg = msgb.decode()
                print('From Cloud server: %s' % msg)
                if msg != '00':
                    return msg


def getNatType():
    Type, ip, port = '', '', ''
    dc1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dc1.settimeout(0.5)     # 500ms
    # FC detect
    retry = 0
    while not Type and retry < 3:
        dc1.sendto("FC detect".encode(), (HOST1, s1p1))
        try:
            _, addr = dc1.recvfrom(BUFFSIZE)
            if addr == (HOST2, s2p1):
                Type = FCNat
                _, ip, port = _.decode().split("'")
        except socket.timeout:
            retry += 1   # Not FC Nat
        # ARC detect
    retry = 0
    while not Type and retry < 3:
        dc1.sendto("ARC detect".encode(), (HOST1, s1p1))
        try:
            _, addr = dc1.recvfrom(BUFFSIZE)
            if addr == (HOST1, s1p2):
                Type = ARCNat
                _, ip, port = _.decode().split("'")
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
                Type = SymNat
            else:
                Type = PRCNat
            _, ip, port = s1Data1.decode().split("'")
        except socket.timeout:
            if retry >= 2:
                print('Timeout: something error!')
            retry += 1
            
    print('Public IP:', ip)
    print('Public Port:', port[2:-1])
    return Type

if __name__ == '__main__':
    natType = getNatType()
    print('Nat Type: %s' % natType)
    selfData = {'account': "ixjhuang@outlook.com",
                'passwd': "raspiot",
                'nattype': natType}
    peerUser(selfData)
