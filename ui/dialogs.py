# coding: utf-8
import os, sys
import wx
import wx.lib.sized_controls as sc
import logfile

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
        data = {'date': self.date.GetValue(),
                'cate': self.cate.GetValue(),
                'num': self.num.GetValue(),
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
        data = {'date': self.date.GetValue(),
                'cate': self.cate.GetValue(),
                'pay': self.pay.GetValue(),
                'num': self.num.GetValue(),
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



