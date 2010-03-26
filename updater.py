# coding: utf-8
import os, sys
import urllib, urlparse, httplib
import socket, urllib2, time
import shutil, zipfile, select
import traceback, md5
import wx
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
     ENOTCONN, ESHUTDOWN, EINTR, EISCONN, errorcode
import version
from ui import logfile, config, i18n

home  = os.path.dirname(os.path.abspath(sys.argv[0]))
cf = config.Configure()
langdir = os.path.join(home, 'lang')
try:
    i18n.install(langdir, [cf['lang']])
except:
    i18n.install(langdir, ['en_US'])
    cf['lang'] = 'en_US'
    cf.dump()


class BackupError (Exception):
    pass

class InstallError (Exception):
    pass


def sumfile(filename):
    m = md5.new()
    fobj = open(filename, 'rb')
    while True:
        d = fobj.read(8086)
        if not d:
            break
        m.update(d)
    fobj.close()
    return m.hexdigest()

class Downloader:
    def __init__(self, url, savepath, callback):
        self.url   = url
        self.local = savepath
        self.localsize = 0
        self.callback = callback
        
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

    def getdata(self, length):
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
                rate = float(self.filesize - length + num) / self.filesize
                going, skip = self.callback.Update(200 + rate * 700, _('Download package') + '... %.2d%%' % (rate * 100))
                if not going:
                    f.close()
                    return
        except Exception, e:
            logfile.info(traceback.format_exc()) 

        f.close()

    def download(self):
        status, reason, headers = self.getheader(0)
        self.filesize = int(headers.getheader('Content-Length'))
        self.callback.Update(150, _('Package size') + ': ' + str(self.filesize))
        logfile.info('local size:', self.localsize, 'http size:', self.filesize)
        
        if self.filesize == self.localsize:
            return

        if self.localsize > self.filesize:
            self.localsize = 0
            os.remove(self.local)
            
        status, reason, headers = self.getheader(self.localsize)
        self.callback.Update(200, _('Download package') + ' ... 0%')
        self.getdata(self.filesize - self.localsize)


class Updater:
    def __init__(self, callback):
        self.home  = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.callback = callback 
        if sys.platform == 'win32':
            self.tmpdir = os.path.join(self.home, 'tmp')
        else:
            self.tmpdir = os.path.join(os.environ['HOME'], '.youmoney', 'tmp')

        if not os.path.isdir(self.tmpdir):
            os.mkdir(self.tmpdir)

        self.info = {}
        self.error_info = '' 
        self.openinfo()

    def openinfo(self):
        socket.setdefaulttimeout(30)
        updatefile = ['http://www.pythonid.com/youmoney/update2.txt', 
                      'http://youmoney.googlecode.com/files/update2.txt']
        num = 0
        for url in updatefile:
            self.callback.Update(50 * num, _('Download update.txt') + '...')
            logfile.info('get:', url)
            try:
                op = urllib2.urlopen(url)
                lines = op.readlines()
            except:
                logfile.info(traceback.format_exc())
                num += 1
                continue
            #logfile.info(lines)

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
        self.callback.Update(100)

    def download(self):
        verstr = self.info['version']
        if int(version.VERSION.replace('.','')) >= int(verstr.replace('.', '')):
            logfile.info('not need update:', version.VERSION, verstr)
            self.error_info = _('Not need update:') + verstr
            return

        if sys.platform == 'darwin' and not self.home.startswith(os.environ['HOME']):
            logfile.info('auto update not support binary on Mac OS X.')
            self.error_info = _('Mac OS X binary version dose not support the automatic update.')
            return

        prefix = 'http://youmoney.googlecode.com/files/'
        noinstallfile = prefix + 'YouMoney-noinstall-%s.zip' % (verstr)
        srcfile = prefix + 'YouMoney-src-%s.zip' % (verstr)

        srcmainfile = os.path.join(self.home, 'youmoney.py')
        fileurl = srcfile
        if os.path.isfile(srcmainfile):
            if sys.platform.startswith('linux') and self.home.startswith('/usr/share'):
                logfile.info('Linux rpm and deb install not support auto update')
                self.err_info = _('Linux rpm and deb install does not support the automaitc update.')
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
                self.error_info = _('Mac OS X binary version dose not support the automatic update.')
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
                dw = Downloader(fileurl, filepath, self.callback)
                dw.download()
            except:
                logfile.info(traceback.format_exc())
                count -= 1
                continue 
            break
        
        self.callback.Update(900, _('Validate package') + '...')
        size = os.path.getsize(filepath)
        if dw.filesize > size:
            self.error_info = _('Package size is too small. Try update again.')
            return

        md5str = sumfile(filepath)
        name = os.path.basename(fileurl)
        logfile.info('file md5:', md5str, self.info[name])
        if md5str == self.info[name]:
            logfile.info('file md5 check ok!')
            return filepath
        elif size >= dw.filesize:
            logfile.info('file md5 check failed. remove')
            os.remove(filepath)
            self.error_info = _('Package md5 is error! Try update again.')
            return
    
    def install(self, filename):
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

            logfile.info('install:', info.filename, 'to:', newpath)
        f.close()

    def backup(self):
        backdir = os.path.join(self.home, 'tmp', 'backup') 
        if os.path.isdir(backdir):
            shutil.rmtree(backdir)
        os.mkdir(backdir)
        
        allfiles = []
        
        for topdir in os.listdir(self.home):
            if topdir in ['.hg', 'tmp'] or topdir.endswith(('.swp', '.log')) or topdir.find('.backup.') > 0:
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
                        shutil.copyfile(fpath, newpath)
                        allfiles.append(fpath)
                        logfile.info('copy:', fpath, newpath)
            else:
                newpath = os.path.join(self.home, 'tmp', 'backup', toppath[len(self.home):].lstrip(os.sep))
                newdir = os.path.dirname(newpath)
                if not os.path.isdir(newdir):
                    os.makedirs(newdir)
                shutil.copyfile(toppath, newpath)
                allfiles.append(toppath)
                logfile.info('copy:', toppath, newpath)
 
        for fname in allfiles:
            logfile.info('remove file:', fname)
            try:
                os.remove(fname)
            except:
                newname = fname + '.backup.' + str(time.time())
                logfile.info('rename:', newname)
                os.rename(fname, newname)
         
    
    def close_youmoney(self):
        maxc = 30
        issend = False
        socket.setdefaulttimeout(30)
        while  maxc > 0:
            logfile.info('try connect to youmoney...')
            self.callback.Update(950)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setblocking(0)
                ret = sock.connect_ex(('127.0.0.1', 9596))
                #logfile.info('connect: ', ret) 

                if ret in [EINPROGRESS, EALREADY, EWOULDBLOCK]:
                    checkmax = 4
                    while checkmax > 0:
                        logfile.info('checkmax:', checkmax)
                        self.callback.Update(950)
                        r = [sock]
                        try:
                            r, w, e = select.select(r, [], [], 0.5)
                        except select.error, err:
                            logfile.info('select error:', err[0], err[1])
                            if err[0] == EINTR:
                                continue
                            raise IOError, 'connect error' 
                        logfile.info(r, w, e)
                        if sock in r:
                            break
                        else:
                            checkmax -= 1
                    else:
                        raise IOError, 'connect error' 
                else:
                    raise IOError, 'connect error'
                sock.setblocking(1)
            except:
                sock.close()
                logfile.info(traceback.format_exc())
                return True
            self.callback.Update(950)
            logfile.info('connect ok!') 
            if not issend:
                sockfile = sock.makefile()
                line = sockfile.readline()
                logfile.info('read:', line.strip()) 
                if not line.startswith('YouMoney'):
                    sock.close()
                    return False
                else:
                    sockfile.write('update\r\n')
                    sockfile.flush()
                    line = sockfile.readline()
                    logfile.info('read:', line.strip())
                    sock.close()

                    issend = True
            else:
                sock.close()
            time.sleep(2)


    def rollback(self):
        backhome = os.path.join(self.home, 'tmp', 'backup')

        for root,dirs,files in os.walk(backhome):
            for fname in files:
                fpath = os.path.join(root, fname)
                dstpath = self.home + fpath[len(backhome):]
                try:
                    shutil.copyfile(fpath, dstpath)
                except:
                    logfile.info(traceback.format_exc())
                logfile.info('rollback file:', fpath, dstpath)


class UpdaterApp (wx.App):
    def __init__(self):
        wx.App.__init__(self, 0)

    def OnInit(self):
        max = 1000
        dlg = wx.ProgressDialog(_("YouMoney Updater"), _("Updating") + "...",
                               maximum = max,parent=None,
                               style = wx.PD_CAN_ABORT| wx.PD_APP_MODAL
                                | wx.PD_ELAPSED_TIME| wx.PD_REMAINING_TIME)

        up = Updater(dlg)
        filepath = None
        errorinfo = ''
        try:
            dlg.Update(0, _('Updating') + '...')
            filepath = up.download()
            dlg.Update(950, _('Close YouMoney') + '...')
            if filepath:
                try:
                    up.close_youmoney()
                    dlg.Update(950, _('Backup old data') + '...')
                    up.backup()
                    up.install(filepath)
                except Exception, e:
                    errorinfo = _('Update failed!') + ' ' + str(e)
                    logfile.info(traceback.format_exc())
                    up.rollback()
                else:
                    os.remove(filepath)
        except:
            logfile.info(traceback.format_exc())

        if errorinfo:
            dlg.Update(1000, errorinfo)
        else:
            if filepath:
                dlg.Update(1000, _('Update complete!'))
            else:
                going, skip = dlg.Update(999)
                if going:
                    if up.error_info:
                        dlg.Update(1000, up.error_info)
                    else:
                        dlg.Update(1000, _('Update failed!'))
                else:
                    dlg.Update(1000, _('Update cancled!'))
        dlg.Destroy()
         
        return True


def main():
    logname = os.path.join(home, 'youmoney.update.log')
    logfile.install(logname)
    #logfile.install('stdout')

    app = UpdaterApp()
    app.MainLoop()


if __name__ == '__main__':
    main()





