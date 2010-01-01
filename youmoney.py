# coding: utf-8
import os, sys
import wx
sys.path.insert(0, os.path.join(os.getcwd(), "ui"))
import i18n
i18n.install("lang", ['zh_CN', 'en_US'])


import window, logfile

VERSION = "YouMoney 0.2"

class MyCash (wx.App):
    def __init__(self):
        wx.App.__init__(self, 0)


    def OnInit(self):
        self.frame = window.MainFrame(None, 101, VERSION)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)

        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        
        return True


    def OnActivate(self, event):
        if event.GetActive():
            pass

        event.Skip()


def main():
    filename = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "youmoney.log")
    logfile.install(filename)
    app = MyCash()
    app.MainLoop()


if __name__ == '__main__':
    main()


