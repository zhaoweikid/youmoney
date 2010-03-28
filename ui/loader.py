import wx, cStringIO
import string, sys, os

def load_bitmap(ipath):
    return wx.BitmapFromImage(wx.ImageFromStream(cStringIO.StringIO(open(ipath,'rb').read())))

def load_image(ipath):
    return wx.ImageFromStream(cStringIO.StringIO(open(ipath,'rb').read()))
    

