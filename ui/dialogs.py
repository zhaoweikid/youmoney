# coding: utf-8
import os, sys, string, re
import wx
import wx.lib.sized_controls as sc
import wx.lib.hyperlink as hl
import logfile

class DigitValidator(wx.PyValidator):
    def __init__(self, pyVar=None):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return DigitValidator()

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()

        for x in val:
            if x != '.' and x not in string.digits:
                return False

        return True

    def OnChar(self, event):
        key = event.GetKeyCode()
        print 'key:', key
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if key == '.' or chr(key) in string.digits:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        return


class IncomeDialog (sc.SizedDialog):
    def __init__(self, parent, readydata):
        sc.SizedDialog.__init__(self, None, -1, _('Add income item'), 
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        self.data = readydata

        panel = self.GetContentsPane()
        panel.SetSizerType("form")
         
        wx.StaticText(panel, -1, _('Date:'))
        #self.date = wx.DatePickerCtrl(panel, size=(120, -1), style=wx.DP_DROPDOWN|
        #            wx.DP_SHOWCENTURY|wx.DP_ALLOWNONE)
        logfile.info('year:', readydata['year'], ' month:', readydata['month'])

        tm = wx.DateTime()
        tm.Set(readydata['day'], readydata['month']-1, readydata['year'])
        self.date = wx.GenericDatePickerCtrl(panel, dt=tm, size=(120, -1), style=wx.DP_DROPDOWN|
                    wx.DP_SHOWCENTURY|wx.DP_ALLOWNONE)

        
        wx.StaticText(panel, -1, _('Category:'))
        items = readydata['cates']
        self.cate = wx.ComboBox(panel, -1, readydata['cate'], (90,50), (160,-1), items, wx.CB_DROPDOWN)

        wx.StaticText(panel, -1, _('Money:'))
        self.num = wx.TextCtrl(panel, -1, str(readydata['num']), size=(125, -1))

        wx.StaticText(panel, -1, _('Explain:'))
        self.explain = wx.TextCtrl(panel, -1, readydata['explain'], size=(220,100), style=wx.TE_MULTILINE)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        self.SetMinSize(wx.Size(300, 250))


        self.Fit()

    def values(self):
        num = self.num.GetValue()
        ret = re.search(u'^[0-9]+(\.[0-9]+)?', num)
        if not ret:
            numstr = '0'
        else:
            numstr = ret.group()

        data = {'date': self.date.GetValue(),
                'cate': self.cate.GetValue(),
                'num': numstr,
                'explain': self.explain.GetValue(),
                'mode': self.data['mode']}
        if self.data.has_key('id'):
            data['id'] = self.data['id']
        return data


class PayoutDialog (sc.SizedDialog):
    def __init__(self, parent, readydata):
        sc.SizedDialog.__init__(self, None, -1, _('Add payout item'), 
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        self.data = readydata
        
        panel = self.GetContentsPane()
        panel.SetSizerType("form")
         
        wx.StaticText(panel, -1, _('Date:'))
        #self.date = wx.DatePickerCtrl(panel, size=(120, -1), style=wx.DP_DROPDOWN|
        tm = wx.DateTime()
        tm.Set(readydata['day'], readydata['month']-1, readydata['year'])
        self.date = wx.GenericDatePickerCtrl(panel, dt=tm, size=(120, -1), style=wx.DP_DROPDOWN|
                    wx.DP_SHOWCENTURY|wx.DP_ALLOWNONE)

        
        wx.StaticText(panel, -1, _('Category:'))
        items = readydata['cates']
        self.cate = wx.ComboBox(panel, -1, readydata['cate'], (90,50), (160,-1), items, wx.CB_DROPDOWN)

        wx.StaticText(panel, -1, _('Payment:'))
        items = [_('Cash'), _('Credit Card')]
        self.pay = wx.ComboBox(panel, -1, readydata['pay'], (90,50), (160,-1), items, wx.CB_DROPDOWN)


        wx.StaticText(panel, -1, _('Money:'))
        self.num = wx.TextCtrl(panel, -1, str(readydata['num']), size=(125, -1))

        wx.StaticText(panel, -1, _('Explain:'))
        self.explain = wx.TextCtrl(panel, -1, readydata['explain'], size=(220,100), style=wx.TE_MULTILINE)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        self.SetMinSize(wx.Size(300, 250))


        self.Fit()
    
    def values(self):
        num = self.num.GetValue()
        ret = re.search('^[0-9]+(\.[0-9]+)?', num)
        if not ret:
            numstr = '0'
        else:
            numstr = ret.group()

        data = {'date': self.date.GetValue(),
                'cate': self.cate.GetValue(),
                'pay': self.pay.GetValue(),
                'num': numstr,
                'explain': self.explain.GetValue(),
                'mode': self.data['mode']}
        if self.data.has_key('id'):
            data['id'] = self.data['id']
 
        return data

class CategoryDialog (sc.SizedDialog):
    def __init__(self, parent, readydata):
        self.data = readydata
        #print 'ready:', readydata
        sc.SizedDialog.__init__(self, None, -1, _('Add Category'), 
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent

        panel = self.GetContentsPane()
        panel.SetSizerType("form")
       
        wx.StaticText(panel, -1, _("Type:"))
        items = [_('Payout'), _('Income')]
        self.catetype = wx.ComboBox(panel, -1, readydata['catetype'], (90,50), (160,-1), items, wx.CB_DROPDOWN)

        wx.StaticText(panel, -1, _("Category:"))
        self.cate = wx.TextCtrl(panel, -1, readydata['cate'], size=(125, -1))


        wx.StaticText(panel, -1, _('Higher Category:'))
        items = readydata['cates'][readydata['catetype']]
        self.upcate = wx.ComboBox(panel, -1, readydata['upcate'], (90,50), (160,-1), items, wx.CB_DROPDOWN)


        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 170))

        self.Fit()

        self.Bind(wx.EVT_COMBOBOX, self.OnChoose, self.catetype)
    
    def OnChoose(self, event):
        value = self.catetype.GetValue()
        self.upcate.Clear()
        for x in self.data['cates'][value]:
            self.upcate.Append(x)
        self.upcate.SetValue(self.data['cates'][value][0])
        #self.upcate.SetValue(self.data['cates'][value])

    
    def values(self):
        data = {'catetype': self.catetype.GetValue(), 
                'cate': self.cate.GetValue(), 
                'upcate': self.upcate.GetValue(),
                'mode': self.data['mode']} 
        if self.data.has_key('id'):
            data['id'] = self.data['id']
 
        return data


class UpdateDialog (sc.SizedDialog):
    def __init__(self, parent, version):
        sc.SizedDialog.__init__(self, None, -1, _('Update'), 
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent

        panel = self.GetContentsPane()
        panel.SetSizerType("vertical")

        wx.StaticText(panel, -1, _('Found new version:') + ' YouMoney-%s' % (version))
        hl.HyperLinkCtrl(panel, wx.ID_ANY, _("Open download page"),URL="http://code.google.com/p/youmoney/downloads/list")
                
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 170))

        self.Fit()



