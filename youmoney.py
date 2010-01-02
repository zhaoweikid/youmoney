# coding: utf-8
import os, sys
import wx
sys.path.insert(0, os.path.join(os.getcwd(), "ui"))
import i18n
i18n.install("lang", ['zh_CN', 'en_US'])
import window, logfile, version


class YouMoney (wx.App):
    def __init__(self):
        wx.App.__init__(self, 0)

    def OnInit(self):
        self.frame = window.MainFrame(None, 101, 'YouMoney ' + version.VERSION)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)

        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        
        return True

    def OnActivate(self, event):
        if event.GetActive():
            pass

        event.Skip()


def main():
    home = os.path.dirname(os.path.abspath(sys.argv[0]))
    datadir = os.path.join(home, 'data')
    if not os.path.isdir(datadir):
        os.mkdir(datadir)
    filename = os.path.join(home, "youmoney.log")
    logfile.install(filename)
    app = YouMoney()
    app.MainLoop()


if __name__ == '__main__':
    main()


