# coding: utf-8
import os, sys
import urllib, urlparse, httplib
import socket, urllib2
import shutil, zipfile
import traceback, md5
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

        self.h.endheaders()
         
        return self.h.getreply()

    def getdata(self, length, callback=None):
        logfile.info('length:', length)
        f = open(self.local, 'a+b')
        num = 0 
        bufsize = 8192
        try:     
            while True:
                leave = length - num
                if leave < bufsize:
                    bufsize = leave
                data = self.h.file.read(bufsize)
                if not data:
                    break
                num += len(data)
                f.write(data)
                logfile.info('download size:', num)
        except Exception, e:
            logfile.info(traceback.format_exc()) 

        f.close()

    def download(self):
        status, reason, headers = self.getheader(0)
        self.filesize = int(headers.getheader('Content-Length'))
        logfile.info('local size:', self.localsize, 'http size:', self.filesize)
        
        if self.filesize == self.localsize:
            return

        if self.localsize > self.filesize:
            self.localsize = 0
            os.remove(self.local)
            
        status, reason, headers = self.getheader(self.localsize)
        self.getdata(self.filesize - self.localsize)


class Updater:
    def __init__(self):
        self.home  = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        if sys.platform == 'win32':
            self.tmpdir = os.path.join(self.home, 'tmp')
        else:
            self.tmpdir = os.path.join(os.environ['HOME'], '.youmoney', 'tmp')

        if not os.path.isdir(self.tmpdir):
            os.mkdir(self.tmpdir)

        self.info = {}
        
        self.openinfo()

    def openinfo(self):
        socket.setdefaulttimeout = 30
        updatefile = ['http://www.pythonid.com/youmoney/update2.txt', 
                      'http://youmoney.googlecode.com/files/update2.txt']

        for url in updatefile:
            logfile.info('get:', url)
            try:
                op = urllib2.urlopen(url)
                lines = op.readlines()
            except:
                logfile.info(traceback.format_exc())
                continue
        
            logfile.info(lines)

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                
                parts = line.split('\t')
                self.info[parts[0]] = parts[1]
             
            return

        raise IOError, 'get update.txt error!'


    def download(self, verstr):
        if int(version.VERSION.replace('.','')) >= int(verstr.replace('.', '')):
            logfile.info('not need update:', version.VERSION, verstr)
            return

        if sys.platform == 'darwin':
            logfile.info('auto update not support Mac OS X.')
            return

        prefix = 'http://youmoney.googlecode.com/files/'
        noinstallfile = prefix + 'YouMoney-noinstall-%s.zip' % (verstr)
        srcfile = prefix + 'YouMoney-src-%s.zip' % (verstr)

        srcmainfile = os.path.join(self.home, 'youmoney.py')
        fileurl = srcfile
        if os.path.isfile(srcmainfile):
            if sys.platform.startswith('linux') and self.home.startswith('/usr/share'):
                logfile.info('Linux rpm and deb install not support auto update')
                return
            fileurl = srcfile
        else:     
            if sys.platform == 'win32':
                exe = os.path.join(self.home, 'youmoney.exe')
                if os.path.isfile(exe):
                    fileurl = noinstallfile
                else:
                    fileurl = srcfile
            elif sys.platform == 'darwin':
                logfile.info('Mac OS X not support binary auto update.')
                return
            elif sys.platform.startswith('linux'):
                fileurl = srcfile
        
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
        name = os.path.basename(fileurl)

        if md5str == self.info[name]:
            logfile.info('file md5 check ok!')
            return filepath
        else:
            logfile.info('file md5 check failed. remove')
            os.remove(filepath)
            return
    
    def install(self, filename):
        self.backup()
        issrc = False
        if filename.find('src') > 0:
            issrc = True

        f = zipfile.ZipFile(filename, 'r')
        for info in f.infolist():
            if info.file_size == 0:
                continue
            filepath = info.filename
            if not issrc and filepath.find('/.hg/') > 0:
                continue
            pos = filepath.find('/')
            newpath = os.path.join(self.home, filepath[pos+1:].replace('/', os.sep))
            newdir = os.path.dirname(newpath)

            if not os.path.isdir(newdir):
                os.mkdirs(newdir)

            newf = open(newpath, 'wb')
            newf.write(f.read(filepath))
            newf.close()

            logfile.info('copy:', info.filename, 'to:', newpath)
        f.close()

    def backup(self):
        backdir = os.path.join(self.home, 'tmp', 'backup') 
        if os.path.isdir(backdir):
            shutil.rmtree(backdir)

        os.mkdir(backdir)
        
        for topdir in os.listdir(self.home):
            if topdir in ['.hg', 'tmp'] or topdir.endswith(('.swp', '.log')):
                continue
            toppath = os.path.join(self.home, topdir)
            if os.path.isdir(toppath):
                for root,dirs,files in os.walk(toppath):
                    for fname in files:
                        fpath = os.path.join(root, fname)
                        if fpath.endswith('.swp'):
                            continue
                        newpath = os.path.join(self.home, 'tmp', 'backup', fpath[len(self.home):].lstrip(os.sep))
                        newdir = os.path.dirname(newpath)
                        if not os.path.isdir(newdir):
                            os.makedirs(newdir)
                        shutil.move(fpath, newpath)
                        logfile.info('move:', fpath, newpath)
            else:
                newpath = os.path.join(self.home, 'tmp', 'backup', toppath[len(self.home):].lstrip(os.sep))
                newdir = os.path.dirname(newpath)
                if not os.path.isdir(newdir):
                    os.makedirs(newdir)
                shutil.move(toppath, newpath)
                logfile.info('move:', fpath, newpath)
 


def main():
    verstr = sys.argv[1]
    home  = os.path.dirname(os.path.abspath(sys.argv[0]))
    logname = os.path.join(home, 'youmoney.update.log')
    #logfile.install(logname)
    logfile.install('stdout')

    up = Updater()
    try:
        filepath = up.download(verstr)
        if filepath:
            up.install(filepath)
    except:
        logfile.info(traceback.format_exc())

if __name__ == '__main__':
    main()





