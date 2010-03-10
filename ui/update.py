# coding: utf-8
import os, sys
import socket, md5
import urllib, urllib2, httplib
import urlparse
import version
import logfile, event
import wx

def sumfile(filename):
    m = md5.new()
    fobj = open(filename, 'r')
    while True:
        d = fobj.read(8086)
        if not d:
            break
        m.update(d)
    fobj.close()
    return m.hexdigest()


class Downloader:
    def __init__(self, url, savepath):
        self.url   = url
        self.local = savepath
        self.localsize = 0
        #self.home  = os.path.dirname(os.path.abspath(sys.argv[0]))
        #self.tmpdir = os.path.join(self.home, 'tmp')

        #if not os.path.isdir(self.tmpdir):
        #    os.mkdir(self.tmpdir)
        
        if os.path.isfile(savepath):
            self.localsize = os.path.getsize(savepath)

        parts = urlparse.urlsplit(self.url)
        self.host = parts[1]
        self.relurl = parts[2]

        self.h = None

    def getheader(self, size=0):        
        if self.h:
            self.h.close()

        self.h = httplib.HTTP()
        #self.h.set_debuglevel(1)
        self.h.connect(self.host)
        self.h.putrequest('GET', self.relurl)
        self.h.putheader('Host', self.host)
        self.h.putheader('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)')
        self.h.putheader('Accept', '*/*')
        self.h.putheader('Accept-Language', 'zh-cn')
        self.h.putheader('Connection', 'Keep-Alive')

        if size > 0:
            self.h.putheader('Range', 'bytes=%d-' % (size))

        print self.h._conn._buffer
        self.h.endheaders()
         
        return self.h.getreply()

    def getdata(self):
        f = open(self.local, 'a+b')
        
        try:     
            while True:
                data = self.h.file.read(8192)        
                if not data:
                    break
                f.write(data)
        except Exception, e:
            logfile.info(e) 
            f.close()
            return
        f.close()

    def download(self):
        status, reason, headers = self.getheader(0)
        self.filesize = int(headers.getheader('Content-Length'))
        print self.localsize, self.filesize
        
        if self.filesize == self.localsize:
            return

        if self.localsize > self.filesize:
            self.localsize = 0
            os.remove(self.local)
            
        status, reason, headers = self.getheader(self.localsize)
        self.getdata()

class Update:
    def __init__(self):
        self.updatefile = ['http://www.pythonid.com/youmoney/update.php', 'http://youmoney.googlecode.com/files/update.txt']
        self.home  = os.path.dirname(os.path.abspath(sys.argv[0]))
        if sys.platform.startswith('win32'):
            self.tmpdir = os.path.join(self.home, 'tmp')
        else:
            self.tmpdir = os.path.join(os.environ['HOME'], '.youmoney', 'tmp')

        if not os.path.isdir(self.tmpdir):
            os.mkdir(self.tmpdir)

    def update(self):
        for u in self.updatefile:
            try:
                loginfo('try update file:', u)
                u = u + '?sys=%s' % (sys.platform)
                self.updateone(u)
            except:
                continue
            break

    def updateone(self, fileurl):
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
            return None
        logfile.info('found new version: ', info['version']) 
        return info['version']
    
        fileurl = 'http://youmoney.googlecode.com/files/YouMoney-noinstall-%s.zip' % (info['version'])
        filepath = os.path.join(self.tmpdir, os.path.basename(fileurl))
        logfile.info('try download %s' % fileurl)
        logfile.info('save:', filepath)
        
        count = 3
        while count > 0: 
            try:
                dw = Downloader(fileurl, filepath)
                dw.download()
            except:
                count -= 1
                continue 
            break

        md5str = sumfile(filepath)
        if md5str == info['md5']:
            logfile('file md5 check ok!')
        else:
            logfile('file md5 check failed. remove')
            os.remove(filepath)
 
    def version_diff(self, newver):
        if version.VERSION == newver:
            return 0
        #usever = version.VERSION.split('.')
        #nowver = newver.split('.')
        
        #for i in range(0, len(nowver)):
        #    print nowver[i], usever[i]
        #    if int(nowver[i]) > int(usever[i]):
        #        return 1

        if int(newver.replace('.','')) > int(version.VERSION.replace('.','')):
            return 1
        
        return 0

def check(frame):
    try:
        up = Update()
        ver = up.update()
        if ver:
            evt = event.UpdateNotifyEvent(version=ver)
            wx.PostEvent(frame, evt)
    except Exception, e:
        logfile.info(e)



def main():
    home  = os.path.dirname(os.path.abspath(sys.argv[0]))
    filename = os.path.join(home, "update.log")
    logfile.install(filename)
    
    try:
        up = Update()
        up.update()
    except Exception, e:
        logfile.info(e)


if __name__ == '__main__':
    main()

        

