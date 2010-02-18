# coding: utf-8
import os, sys
import socket
import urllib, urllib2
import version
from ui import logfile

class Update:
    def __init__(self):
        self.updatefile = 'http://youmoney.googlecode.com/files/update.txt'

    def update(self):
        socket.setdefaulttimeout = 30
        fs = urllib2.urlopen(self.updatefile)
        lines = fs.readlines()
        fs.close() 

        info = {}
        for line in lines:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) != 2:
                continue
            info[parts[0]] = parts[1]
    
        if not self.version_diff(info['version']):
            logfile.info('not need update:', info['version'])
            return
        
        filename = 'http://youmoney.googlecode.com/files/YouMoney-noinstall-%s.zip' % (info['version'])
        logfile.info('try download %s' % filename)

        self.download(filename)
        
    def download(self, url):
        filename = os.path.basename(url)



    def version_diff(self, newver):
        if version.VERSION == newver:
            return 0
        usever = version.VERSION.split('.')
        nowver = newver.split('.')
        
        for i in range(0, len(nowver)):
            if nowver[i] > usever[i]:
                return 1
        
        return 0

def main():
    filename = os.path.join(home, "update.log")
    logfile.install(filename)
    
    try:
        up = Update()
        up.update()
    except Exception, e:
        logfile.info(e)


if __name__ == '__main__':
    main()

        

