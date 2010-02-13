# coding: utf-8
import os, sys
import urllib2

class Updater:
    def __init__(self):
        self.url = 'http://youmoney.googlecode.com/files/update.txt'
        self.pyver = sys.version_info[:3]
        
        self.home = os.path.dirname(os.path.abspath(sys.argv[0]))
        f = open(os.path.join(home, 'version.dat'), 'r')
        s = f.readline()
        f.close()

        self.version = int(s.strip().replace('.', ''))

    def update():
        if self.pyver[0] == 2 and self.pyver[1] >= 6:
            uf = urllib2.urlopen(self.url, timeout=30)
        else:
            uf = urllib2.urlopen(self.url)
        s = uf.read()
        info = s.strip().split()
        
        nowver = int(info[0])
        
        if nowver <= self.version:
            return
        
        tmpdir = os.path.join(self.home, 'tmp')
        if not os.path.isdir(tmpdir):
            os.mkdir(tmpdir)

        filename = self.download(info[1], tmpdir):
        self.updatefiles(filename)

    def download(self, url, tmpdir):
        localfile = os.path.join(tmpdir, os.path.basename(url))

        if self.pyver[0] == 2 and self.pyver[1] >= 6:
            uf = urllib2.urlopen(self.url, timeout=30)
        else:
            uf = urllib2.urlopen(self.url)
       
        f = open(localfilem 'wb')
        while True:
            s = uf.read(32768)
            if not s:
                break
            f.write(s)

        f.close()
        return localfile

    def updatefiles(self, filename):
        pass


    



