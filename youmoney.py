#!/usr/bin/python
# coding: utf-8
# YouMoney is a opensource personal finance software
# License: GPL
# Author: zhaoweiakid <zhaoweikid@163.com>
# 感谢 Jacky MA <jackyma1981@gmail.com> 制作的日文支持

import os, sys
import threading
import wx
home = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.insert(0, os.path.join(home, "ui"))
#os.chdir(home)
import i18n, config
config.cf = config.Configure()
langdir = os.path.join(home, "lang")
try:
    i18n.install(langdir, [config.cf['lang']])
except:
    i18n.install(langdir, ['en_US'])
    config.cf['lang'] = 'en_US'
    config.cf.dump()

import window, logfile, version, update


class YouMoney (wx.App):
    def __init__(self):
        wx.App.__init__(self, 0)

    def OnInit(self):
        self.frame = window.MainFrame(None, 101, 'YouMoney ' + version.VERSION)
        self.frame.Show(True)
        self.frame.CenterOnScreen()
        self.SetTopWindow(self.frame)

        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        
        return True

    def OnActivate(self, event):
        if event.GetActive():
            pass

        event.Skip()


def main():
    #home = os.path.dirname(os.path.abspath(sys.argv[0]))
    #datadir = os.path.join(home, 'data')
    #if not os.path.isdir(datadir):
    #    os.mkdir(datadir)
    if sys.platform.startswith('win32'):
        filename = os.path.join(home, "youmoney.log")
        vername  = os.path.join(home, "version.dat")
    else:
        filename = os.path.join(os.environ['HOME'], ".youmoney", "youmoney.log")
        vername  = os.path.join(os.environ['HOME'], ".youmoney", "verion.dat")
    logfile.install(filename)
        
    versionfile = os.path.join(home, '')
    f = open(vername, 'w')
    f.write(version.VERSION)
    f.close()

    app = YouMoney()
    th = threading.Thread(target=update.check, args=(app.frame,))
    th.start()
    app.MainLoop()


if __name__ == '__main__':
    main()


