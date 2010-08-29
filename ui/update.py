# coding: utf-8
import os, sys
import socket
import platform
import json
import traceback, subprocess
import version
import logfile, event, storage, netreq
import wx

def windows_version():
    info = sys.getwindowsversion()
    verstr = '%d.%d.%d' % (info[3], info[0], info[1])
        
    win_version = {'1.4.0':'95', '1.4.10':'98', '1.4.90':'ME', 
                   '2.4.0':'NT', '2.5.0':'2000', '2.5.1':'XP', '2.5.2':'2003',
                   '2.6':'Vista', '2.6.0':'Vista', '2.6.1':'7'}
    
    try:
        winver = 'Windows %s %s %s %s' % (win_version[verstr], platform.version(), str(info[2]), info[4])
    except:
        winver = 'Windows %s %s %s %s' % (verstr, platform.version(), str(info[2]), info[4])

    return winver

def system_version():
    try:
        if sys.platform == 'darwin':
            x = platform.mac_ver()
            info = '%s (Mac OS X %s)' % (platform.platform(), x[0])
        elif sys.platform == 'win32':
            info = windows_version()
        else:
            info = platform.platform()
    except:
        info = platform.platform()
    return info

class Update:
    def __init__(self):
        self.home  = os.path.dirname(os.path.abspath(sys.argv[0]))
        if sys.platform.startswith('win32'):
            self.tmpdir = os.path.join(self.home, 'tmp')
        else:
            self.tmpdir = os.path.join(os.environ['HOME'], '.youmoney', 'tmp')

        if not os.path.isdir(self.tmpdir):
            os.mkdir(self.tmpdir)

    def update(self):
        newver = None
        try:
            info = system_version()
            logfile.info('local system:', info) 
            req = {'act':'checklog', 'sys':sys.platform, 'ver':version.VERSION, 'info':info, 'name':storage.name}
            reqconn = netreq.Request(5)
            header, data = reqconn.docmd(req)
            reqconn.close()

            newver = header.get('version')
            if not self.version_diff(newver):
                logfile.info('not need update:', newver)
                return None
            logfile.info('found new version:', newver)

            return newver
        except:
            logfile.info(traceback.format_exc())

        return newver
  
    def version_diff(self, newver):
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
    #main()
    print windows_version()

        

