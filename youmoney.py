# coding: utf-8
# YouMoney is a opensource personal finance software
# License: GPL
# Author: zhaoweiakid <zhaoweikid@163.com>
# 感谢 Jacky MA <jackyma1981@gmail.com> 制作的日文支持

import os, sys
import wx
sys.path.insert(0, os.path.join(os.getcwd(), "ui"))
import i18n, config
config.cf = config.Configure()
try:
    i18n.install("lang", [config.cf['lang']])
except:
    i18n.install("lang", ['en_US'])
    config.cf['lang'] = 'en_US'
    config.cf.dump()

import window, logfile, version


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
    home = os.path.dirname(os.path.abspath(sys.argv[0]))
    #datadir = os.path.join(home, 'data')
    #if not os.path.isdir(datadir):
    #    os.mkdir(datadir)
    filename = os.path.join(home, "youmoney.log")
    logfile.install(filename)
        
    versionfile = os.path.join(home, '')
    f = open('version.dat', 'w')
    f.write(version.VERSION)
    f.close()

    app = YouMoney()
    app.MainLoop()


if __name__ == '__main__':
    main()


