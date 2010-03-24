# coding: utf-8
import os, sys
import urllib, urlparse, httplib
import traceback
import version
from ui import logfile

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


class Updater:
    def __init__(self, newver):
        self.version = newver
        self.version_int = newver.replace('.', '')
        self.home  = os.path.dirname(os.path.abspath(__file__))
        
        if sys.platform == 'win32':
            self.tmpdir = os.path.join(self.home, 'tmp')
        else:
            self.tmpdir = os.path.join(os.environ['HOME'], '.youmoney', 'tmp')

        if not os.path.isdir(self.tmpdir):
            os.mkdir(self.tmpdir)

    def download(self, version):
        if int(version.VERSION.replace('.','')) >= self.version_int:
            logfile.info('not need update:', version.VERSION, self.version)
            return True

        if sys.platform == 'darwin':
            logfile.info('auto update not support Mac OS X.')
            return False

        prefix = 'http://youmoney.googlecode.com/files/'
        srcfile = os.path.join(self.home, 'youmoney.py')

        if os.path.isfile(srcfile):
            fileurl = prefix + 'YouMoney-src-%s.zip'$ (self.version)
        else:     
            if sys.platform == 'win32':
                exe = os.path.join(self.home, 'youmoney.exe')
                if os.path.isfile(exe):
                    fileurl = prefix + 'YouMoney-noinstall-%s.zip' % (version)
                else:
                    fileurl = prefix + 'YouMoney-src-%s.zip' % (version)
            elif sys.platform == 'darwin':
                fileurl = prefix + 'YouMoney-macosx10.5-%s.app.zip' % (version)
            else:
                fileurl = prefix + 'YouMoney-src-%s.zip' % (version)
        
        filepath = os.path.join(self.tmpdir, os.path.basename(fileurl))
        self.path = filepath
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
            logfile.info('file md5 check ok!')
            return True
        else:
            logfile.info('file md5 check failed. remove')
            os.remove(filepath)
            return False
    
    def install(self):
        pass


def main():
    version = sys.argv[1]
    home  = os.path.dirname(os.path.abspath(__file__))
    logname = os.path.join(home, 'youmoney.update.log')
    logfile.install(logname)
    up = Updater()
    try:
        up.download(version)
    except:
        logfile.info(traceback.format_exc())

if __name__ == '__main__':
    main()





