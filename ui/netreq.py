# coding: utf-8
import os, sys
import json
import traceback
import socket
import logfile, config

conn = None

class Request:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.addr = config.cf['server'].split(':')
        self.addr[0] = str(self.addr[0])
        if len(self.addr) == 1:
            self.addr.append(9900)
        else:
            self.addr[1] = int(self.addr[1])
        self.addr = tuple(self.addr)
        logfile.info('req addr:', self.addr)
        self.conn = None
        self.connect()

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.settimeout(self.timeout)
        self.conn.connect(self.addr)
        self.cfile = self.conn.makefile()
    
    def send(self, x, data=None):
        if not data:
            s = json.dumps(x) + '\r\n'
        else:
            x['len'] = len(data)
            s = json.dumps(x).encode('utf-8') + '\r\n' + data

        self.cfile.write(s)
        self.cfile.flush()

    def recv(self):
        line = self.cfile.readline()
        header = json.loads(line)
        xlen = header.get('len', 0)
        if xlen > 0:
            x = self.cfile.read(xlen)
        else:
            x = ''
        return header, x    

    def docmd(self, x, data=None, trycount=2):
        while trycount > 0:
            try:
                self.send(x, data)
            except:
                logfile.info(traceback.format_exc())
                self.conn.close()
                self.connect()
                trycount -= 1
                continue
            break

        return self.recv()

    def noop(self):
        self.send({'act':'noop'})

    def close(self):
        self.cfile.close()
        self.conn.close()




