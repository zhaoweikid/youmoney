#!/usr/bin/python
# coding: utf-8
# YouMoney is a opensource personal finance software
# License: GPL
# Author: zhaoweiakid <zhaoweikid@163.com>
# 感谢 Jacky MA <jackyma1981@gmail.com> 制作的日文支持

import os, sys
import threading
import wx
import ui

home = os.path.dirname(os.path.abspath(sys.argv[0]))

cf = ui.config.Configure()
langdir = os.path.join(home, "lang")
try:
    ui.i18n.install(langdir, [cf['lang']])
except:
    ui.i18n.install(langdir, ['en_US'])
    cf['lang'] = 'en_US'
    cf.dump()

import version
from ui import window, logfile, update, task, loader


class YouMoneySplashScreen (wx.SplashScreen):
    def __init__(self, parent):
        global home
        self.parent = parent
        bmp = loader.load_bitmap(os.path.join(home, 'images', 'splash.png'))
        wx.SplashScreen.__init__(self, bmp, wx.SPLASH_CENTER_ON_SCREEN|wx.SPLASH_TIMEOUT, 5000, None, -1)
        self.fc = wx.FutureCall(1000, self.ShowMain)


    def OnClose(self, event):
        event.Skip()
        self.Hide()

        if self.fc.IsRunning():
            self.fc.Stop()
            self.ShowMain()

    def ShowMain(self):
        global cf
        self.frame = window.MainFrame(None, 101, 'YouMoney ' + version.VERSION, cf)
        self.frame.CenterOnScreen()
        self.parent.SetTopWindow(self.frame)
        self.frame.Show(True)


class YouMoney (wx.App):
    def __init__(self):
        wx.App.__init__(self, 0)

    def OnInit2(self):
        global cf
        self.frame = window.MainFrame(None, 101, 'YouMoney ' + version.VERSION, cf)
        self.frame.CenterOnScreen()
        self.SetTopWindow(self.frame)
        self.frame.Show(True)

        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        
        return True

    def OnInit(self):
        splash = YouMoneySplashScreen(self)
        #self.frame = splash.frame
        splash.Show()

        return True

    def OnActivate(self, event):
        if event.GetActive():
            pass

        event.Skip()


def main():
    if sys.platform.startswith('win32'):
        filename = os.path.join(home, "youmoney.log")
        vername  = os.path.join(home, "version.dat")
    else:
        filename = os.path.join(os.environ['HOME'], ".youmoney", "youmoney.log")
        vername  = os.path.join(os.environ['HOME'], ".youmoney", "verion.dat")
    logfile.install(filename)
        
    f = open(vername, 'w')
    f.write(version.VERSION)
    f.close()

    th = task.Task()
    th.start()
 
    app = YouMoney()
    app.MainLoop()


if __name__ == '__main__':
    main()


