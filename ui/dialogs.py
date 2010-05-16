# coding: utf-8
import os, sys, string, re
import wx
import wx.lib.sized_controls as sc
import wx.lib.hyperlink as hl
import urllib, urllib2, json
import logfile

class IncomeDialog (sc.SizedDialog):
    def __init__(self, parent, readydata):
        if readydata['mode'] == 'insert':
            title = _('Add income item')
        else:
            title = _('Edit income item')

        sc.SizedDialog.__init__(self, None, -1, title, 
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
        self.cate = wx.ComboBox(panel, -1, readydata['cate'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)

        wx.StaticText(panel, -1, _('Money:'))
        self.num = wx.TextCtrl(panel, -1, str(readydata['num']), size=(125, -1))

        wx.StaticText(panel, -1, _('Explain:'))
        self.explain = wx.TextCtrl(panel, -1, readydata['explain'], size=(220,100), style=wx.TE_MULTILINE)

        wx.StaticText(panel, -1, '')
        self.reuse = wx.CheckBox(panel, -1, _("Not close dialog, continue."))

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 250))

        self.Fit()

    def values(self):
        num = self.num.GetValue()
        ret = re.search(u'^[0-9]+(\.[0-9]+)?', num)
        if not ret:
            ret = re.search(u'\.[0-9]+', num)
            if ret:
                numstr = '0' + num
            else:
                numstr = '0'
        else:
            numstr = ret.group()

        data = {'date': self.date.GetValue(),
                'cate': self.cate.GetValue(),
                'num': numstr,
                'explain': self.explain.GetValue(),
                'reuse': self.reuse.GetValue(),
                'mode': self.data['mode']}
        if self.data.has_key('id'):
            data['id'] = self.data['id']
        return data

    def ClearForReinput(self):
        self.num.Clear()
        self.explain.Clear()
        self.date.SetFocus()



class PayoutDialog (sc.SizedDialog):
    def __init__(self, parent, readydata):
        if readydata['mode'] == 'insert':
            title = _('Add payout item')
        else:
            title = _('Edit payout item')
        sc.SizedDialog.__init__(self, None, -1, title, 
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
        self.cate = wx.ComboBox(panel, -1, readydata['cate'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)

        wx.StaticText(panel, -1, _('Payment:'))
        items = [_('Cash'), _('Credit Card')]
        self.pay = wx.ComboBox(panel, -1, readydata['pay'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)

        wx.StaticText(panel, -1, _('Money:'))
        self.num = wx.TextCtrl(panel, -1, str(readydata['num']), size=(125, -1))

        wx.StaticText(panel, -1, _('Explain:'))
        self.explain = wx.TextCtrl(panel, -1, readydata['explain'], size=(220,100), style=wx.TE_MULTILINE)

        wx.StaticText(panel, -1, '')
        self.reuse = wx.CheckBox(panel, -1, _("Not close dialog, continue."))
 
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 250))
        self.Fit()
    
    def values(self):
        num = self.num.GetValue()
        ret = re.search('^[0-9]+(\.[0-9]+)?', num)
        if not ret:
            ret = re.search(u'\.[0-9]+', num)
            if ret:
                numstr = '0' + num
            else:
                numstr = '0'
        else:
            numstr = ret.group()

        data = {'date': self.date.GetValue(),
                'cate': self.cate.GetValue(),
                'pay': self.pay.GetValue(),
                'num': numstr,
                'explain': self.explain.GetValue(),
                'reuse': self.reuse.GetValue(),
                'mode': self.data['mode']}
        if self.data.has_key('id'):
            data['id'] = self.data['id']
 
        return data

    def ClearForReinput(self):
        self.num.Clear()
        self.explain.Clear()
        self.date.SetFocus()

class CycleDialog (sc.SizedDialog):
    def __init__(self, parent, readydata):
        if readydata['mode'] == 'insert':
            title = _('Add cycle item')
        else:
            title = _('Edit cycle item')
        sc.SizedDialog.__init__(self, None, -1, title, 
                                style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.data = readydata
        
        panel = self.GetContentsPane()
        panel.SetSizerType("form")
 
        wx.StaticText(panel, -1, _('Note:'))
        self.noteinfo = wx.StaticText(panel, -1, _('Record cycle will automatic add payout or income by every time that you specify.'))

        wx.StaticText(panel, -1, _('Type:'))
        items = readydata['types']
        self.catetype = wx.ComboBox(panel, -1, readydata['type'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)
        
        wx.StaticText(panel, -1, _('Category:'))
        if readydata['type'] == _('Payout'):
            items = readydata['payout_cates']
            self.cate = wx.ComboBox(panel, -1, readydata['payout_cate'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)
        else:
            items = readydata['income_cates']
            self.cate = wx.ComboBox(panel, -1, readydata['income_cate'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)
 
        wx.StaticText(panel, -1, _('Payment:'))
        items = [_('Cash'), _('Credit Card')]
        self.pay = wx.ComboBox(panel, -1, readydata['pay'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)

        wx.StaticText(panel, -1, _('Money:'))
        self.num = wx.TextCtrl(panel, -1, str(readydata['num']), size=(125, -1))

        wx.StaticText(panel, -1, _('Cycle:'))
        items = readydata['cycles']
        self.addtime = wx.ComboBox(panel, -1, readydata['cycle'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)

        wx.StaticText(panel, -1, _('Explain:'))
        self.explain = wx.TextCtrl(panel, -1, readydata['explain'], size=(220,100), style=wx.TE_MULTILINE)

        wx.StaticText(panel, -1, '')
        self.reuse = wx.CheckBox(panel, -1, _("Not close dialog, continue."))
 
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 250))
        self.Fit()

        self.num.SetFocus()
        self.Bind(wx.EVT_COMBOBOX, self.OnChoose, self.catetype)

    def OnChoose(self, event):
        value = self.catetype.GetValue()
        self.cate.Clear()
        self.pay.Clear()
        if value == _('Payout'):
            for x in self.data['payout_cates']:
                self.cate.Append(x)
            self.cate.SetValue(self.data['payout_cate'])

            self.pay.Append(_('Cash'))
            self.pay.Append(_('Credit Card'))
            self.pay.SetValue(_('Cash'))
        else:
            for x in self.data['income_cates']:
                self.cate.Append(x)
            self.cate.SetValue(self.data['income_cate'])

            self.pay.Append(_('Cash'))
            self.pay.SetValue(_('Cash'))
    
    def values(self):
        num = self.num.GetValue()
        ret = re.search('^[0-9]+(\.[0-9]+)?', num)
        if not ret:
            ret = re.search(u'\.[0-9]+', num)
            if ret:
                numstr = '0' + num
            else:
                numstr = '0'
 
        else:
            numstr = ret.group()

        data = {'cate': self.cate.GetValue(),
                'pay': self.pay.GetValue(),
                'type': self.catetype.GetValue(),
                'addtime': self.addtime.GetValue(),
                'num': numstr,
                'explain': self.explain.GetValue(),
                'reuse': self.reuse.GetValue(),
                'mode': self.data['mode']}
        if self.data.has_key('id'):
            data['id'] = self.data['id']
 
        return data

    def ClearForReinput(self):
        self.num.Clear()
        self.explain.Clear()
        self.num.SetFocus()


class CategoryDialog (sc.SizedDialog):
    def __init__(self, parent, readydata):
        self.data = readydata

        if readydata['mode'] == 'insert':
            title = _('Add Category')
        else:
            title = _('Edit Category')

        sc.SizedDialog.__init__(self, None, -1, title, 
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        panel = self.GetContentsPane()
        panel.SetSizerType("form")
       
        wx.StaticText(panel, -1, _("Type:"))
        items = [_('Payout'), _('Income')]
        self.catetype = wx.ComboBox(panel, -1, readydata['catetype'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)

        wx.StaticText(panel, -1, _("Category:"))
        self.cate = wx.TextCtrl(panel, -1, readydata['cate'], size=(125, -1))


        wx.StaticText(panel, -1, _('Higher Category:'))
        items = readydata['cates'][readydata['catetype']]
        self.upcate = wx.ComboBox(panel, -1, readydata['upcate'], (90,50), (160,-1), items, wx.CB_DROPDOWN|wx.CB_READONLY)

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
        hl.HyperLinkCtrl(panel, wx.ID_ANY, _("Open download page"),URL="http://code.google.com/p/youmoney/")
        wx.StaticText(panel, -1, _('Click OK to start the automatic update.'))
                
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 170))
        self.Fit()


class PasswordDialog (sc.SizedDialog):
    def __init__(self, parent):
        sc.SizedDialog.__init__(self, None, -1, _('Set Password'), 
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        panel = self.GetContentsPane()
        panel.SetSizerType("form")
        
        wx.StaticText(panel, -1, "")
        self.warn = wx.StaticText(panel, -1, size=(150, -1))

        wx.StaticText(panel, -1, _("Password:"))
        self.pass1 = wx.TextCtrl(panel, -1, style=wx.TE_PASSWORD, size=(150, -1))

        wx.StaticText(panel, -1, _("Password Again:"))
        self.pass2 = wx.TextCtrl(panel, -1, style=wx.TE_PASSWORD, size=(150, -1))

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 170))
        self.Fit()

    def values(self):
        pass1 = self.pass1.GetValue()
        pass2 = self.pass2.GetValue()
        return {'password1':pass1, 'password2':pass2}

    def set_warn(self, msg):
        self.warn.SetLabel(msg)       

class UserCheckDialog (sc.SizedDialog):
    def __init__(self, parent):
        sc.SizedDialog.__init__(self, None, -1, 'YouMoney ' + _('User Password'), 
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        panel = self.GetContentsPane()
        panel.SetSizerType("form")
        
        wx.StaticText(panel, -1, "")
        self.warn = wx.StaticText(panel, -1, style=wx.ST_NO_AUTORESIZE , size=(150, -1))

        wx.StaticText(panel, -1, _("Password: "))
        self.password = wx.TextCtrl(panel, -1, style=wx.TE_PASSWORD, size=(180, -1))

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 150))
        self.Fit()
        self.password.SetFocus()

    def values(self):
        return {'password': self.password.GetValue()} 

    def set_warn(self, msg):
        self.warn.SetLabel(msg)       


class ImportCateDialog (sc.SizedDialog):
    def __init__(self, parent):
        sc.SizedDialog.__init__(self, None, -1, _('Import Category'), 
                                style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        panel = self.GetContentsPane()
        panel.SetSizerType("vertical")
        
        msg = [_('Import category format:'),
               _('It use csv format.The first row is fields description, not data.'),
               _('This have three fields: main category, sub category, type.'),
               '\n',
               _('Example:'),
               _('Main Category,Sub Category,Type'),
               _('Recreation,KTV,Payout'),
               _('Recreation,Basketball,Payout'),
               _('Public Traffic,,Payout'),
               _('Weges,,Income'),
               '\n'
               ]

        wx.StaticText(panel, -1, '\n'.join(msg))
        
        wx.StaticText(panel, -1, _('Open csv file:'))
        self.filepath = wx.TextCtrl(panel, -1, size=(300, -1))
        self.chfile = wx.Button(panel, -1, _('Browse csv file'))
            
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.chfile)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 170))
        self.Fit()

    def GetPath(self):
        return self.filepath.GetValue()

    def OnButton(self, event):
        dlg = wx.FileDialog(
            self, message=_("Choose csv file:"), defaultDir=os.getcwd(), 
            defaultFile="", wildcard=_("csv file (*.csv)|*.csv"), style=wx.SAVE)
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.filepath.SetValue(path)
        dlg.Destroy()


class ImportDataDialog (sc.SizedDialog):
    def __init__(self, parent):
        sc.SizedDialog.__init__(self, None, -1, _('Import Data'), 
                                style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        panel = self.GetContentsPane()
        panel.SetSizerType("vertical")

        msg = [_('Import data format:'),
               _('It use csv format.The first row is fields description, not data.'),
               _('This have ten fields: Main Category,Sub Category,Money,Payway,Type,Time,Year,Month,Day,Explain.'),
               _('If category is not exists, create.'),
               _('Money is payout number.'),
               _('Payway is Cash or Credit Card.'),
               _('Type is Payout or Income.'),
               _('Time is record create time.'),
               _('Year, Month, Day is pay time.'),
               '\n',
               _('Example:'),
               _('Main Category,Sub Category,Money,Payway,Type,Time,Year,Month,Day,Explain'),
               _('Recreation,KTV,220,Cash,Payout,2010-02-10 18:12:01,2010,2,9,go ktv'),
               _('Public Traffic,,6,Cash,Payout,2010-02-11 10:09:01,2010,2,11,go home by bus'),
               '\n'
               ]

        wx.StaticText(panel, -1, '\n'.join(msg))
        
        wx.StaticText(panel, -1, _('Open csv file:'))
        self.filepath = wx.TextCtrl(panel, -1, size=(300, -1))
        self.chfile = wx.Button(panel, -1, _('Browse csv file'))
            
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.chfile)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 170))
        self.Fit()

    def GetPath(self):
        return self.filepath.GetValue()

    def OnButton(self, event):
        dlg = wx.FileDialog(
            self, message=_("Choose csv file:"), defaultDir=os.getcwd(), 
            defaultFile="", wildcard=_("csv file (*.csv)|*.csv"), style=wx.SAVE)
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.filepath.SetValue(path)
        dlg.Destroy()

class UserPassDialog (sc.SizedDialog):
    def __init__(self, parent, conf, mode='add'):
        if mode == 'add':
            title = _('Sync User Add')
        else:
            title = _('Sync User Password Change')
        super(UserPassDialog, self).__init__(None, -1, title, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.conf = conf
        self.mode = mode

        panel = self.GetContentsPane()
        panel.SetSizerType("form")
    
        wx.StaticText(panel, -1, "")
        self.warn = wx.StaticText(panel, -1, size=(150, -1))

        wx.StaticText(panel, -1, _("Username")+':')
        self.username = wx.TextCtrl(panel, -1, size=(150, -1))

        if mode == 'modify':
            wx.StaticText(panel, -1, _("Old Password")+':')
            self.oldpass = wx.TextCtrl(panel, -1, style=wx.TE_PASSWORD, size=(150, -1))

        wx.StaticText(panel, -1, _("Password:"))
        self.pass1 = wx.TextCtrl(panel, -1, style=wx.TE_PASSWORD, size=(150, -1))

        wx.StaticText(panel, -1, _("Password Again:"))
        self.pass2 = wx.TextCtrl(panel, -1, style=wx.TE_PASSWORD, size=(150, -1))

        if mode == 'modify':
            self.username.SetValue(self.conf['user'])
            self.oldpass.SetValue(self.conf['password'])

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(300, 170))
        self.Fit()

    def values(self):
        user  = self.username.GetValue()
        pass1 = self.pass1.GetValue()
        pass2 = self.pass2.GetValue()
        if self.mode == 'modify':
            return {'username':user, 'password1':pass1, 'password2':pass2, 'oldpass': self.oldpass.GetValue()}
        else:
            return {'username':user, 'password1':pass1, 'password2':pass2}

    def set_warn(self, msg):
        self.warn.SetLabel(msg)       

 
class SyncDialog (sc.SizedDialog):
    def __init__(self, parent, conf):
        super(SyncDialog, self).__init__(None, -1, _('Sync User Data'), style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.conf = conf

        panel = self.GetContentsPane()
        panel.SetSizerType("vertical")
        
        msg = [_('Sync will synchronous user data to server.'),
               _('Then, user can use the same data everywhere.'),
              ]

        s = '\n'.join(msg)
        wx.StaticText(panel, -1, s)
        valuelist = [_('Not Sync'), _('Sync with configure file setting'), _('Sync with username and password')]
        self.syncway = wx.RadioBox(panel, -1, _('Choose Sync Way'), wx.DefaultPosition, wx.DefaultSize, valuelist, 1, wx.RA_SPECIFY_COLS)
        
        self.info = wx.Panel(panel, -1)

        self.create_info()

        wx.StaticText(panel, -1, _('Click OK to start synchronous immediately.'))

        self.select(self.conf['sync_way'])

        self.Bind(wx.EVT_RADIOBOX, self.OnRadioBox, self.syncway)
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.SetMinSize(wx.Size(450, 300))
        self.Fit()


        self.errors = {401: _('user is exist'), 
                       402: _('password error'),
                       403: _('user is not exist'),
                       404: _('username error'), 
                       440: _('internal error')}

    def select(self, choice):
        if choice == '' or choice == 0:
            self.syncway.SetSelection(0)
            self.changepass.Disable()
            s = _('Not sync anything.') + '\n\n'
            self.msg.SetLabel(s)
        elif choice == 'id' or choice == 1:
            self.syncway.SetSelection(1)
            self.changepass.Disable()
        
            msg = [_('This option have the best privacy and security. '), 
                   _('When use YouMoney in other computer, '), 
                   _('you must copy data/youmoney.conf to another.')]
            s = '\n'.join(msg)
            
            self.msg.SetLabel(s)
        else:
            self.syncway.SetSelection(2)
            self.changepass.Enable()
    
            msg = [_('This option have the best conveniency. '), 
                   _('When use YouMoney in other computer, '), 
                   _('you must input username and password to sync data.')]
            s = '\n'.join(msg)
 
            self.msg.SetLabel(s)
            
            if not self.conf['user']:
                self.user_add()
 
    def value(self):
        ret = self.syncway.GetSelection()
        if ret == 1:
            return 'id'
        elif ret == 2:
            return 'user'
        return ''

    def OnRadioBox(self, event):
        self.select(event.GetInt())

    def create_info2(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.msg = wx.StaticText(self.info, -1, '', style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.msg.Wrap(60)
        sizer.Add(self.msg, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        box = wx.FlexGridSizer(0, 2, 0, 0)
        label = wx.StaticText(self.info, -1, _("Username:"))
        box.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.username  = wx.TextCtrl(self.info, -1, self.conf['user'], size=(120, -1))
        box.Add(self.username, 1, wx.ALIGN_CENTER|wx.ALL, 5)
            
        label = wx.StaticText(self.info, -1, _("Password:"))
        box.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.password  = wx.TextCtrl(self.info, -1, self.conf['password'], size=(120, -1))
        box.Add(self.password, 1, wx.ALIGN_CENTER|wx.ALL, 5)

        sizer.Add(box, 1, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.ALL, 5)
          
        self.info.SetSizer(sizer)


    def create_info(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        #self.msg = wx.StaticText(self.info, -1, '', style=wx.ALIGN_LEFT|wx.ST_NO_AUTORESIZE)
        self.msg = wx.StaticText(self.info, -1, '', size=(300, -1), style=wx.ALIGN_LEFT)
        sizer.Add(self.msg, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)

        self.changepass = wx.Button(self.info, -1, _('Change Username/Password'), (20, 80))
        sizer.Add(self.changepass, 1, wx.ALIGN_LEFT|wx.ALL, 5)
        self.info.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.OnChangePassword, self.changepass)

    def user_add(self):
        isok = False
        dlg = UserPassDialog(self, self.conf, 'add')
        while True:
            ret = dlg.ShowModal()
            if ret != wx.ID_OK:
                return
            vals = dlg.values()
            if vals['password1'] != vals['password2']:
                dlg.set_warn(_('Different password.'))
                continue
            url = 'http://%s/sync?action=useradd&ident=%s&user=%s&pass=%s' % \
                    (self.conf['server'], self.conf['id'], urllib.quote(vals['username']), urllib.quote(vals['password1']))
            resp = urllib2.urlopen(url) 
            s = resp.read()
            
            val = json.loads(s)
            errstr = val.get('error')
            if errstr:
                logfile.info(errstr)
                dlg.set_warn(self.errors[val['status']])
                continue
             
            wx.MessageBox(_('User and password are successfully added!'), _('Success'), wx.OK|wx.ICON_INFORMATION)
            self.conf['user'] = vals['username']
            self.conf['password'] = vals['password']
            self.conf.dump()
            isok = True
            break

        dlg.Destroy()
        return isok


    def OnChangePassword(self, event):
        dlg = UserPassDialog(self, self.conf, 'modify')
        while True:
            ret = dlg.ShowModal()
            if ret != wx.ID_OK:
                return
            vals = dlg.values()
            if vals['password1'] != vals['password2']:
                dlg.set_warn(_('Different password.'))
                continue

            url = 'http://%s/sync?action=usermodify&ident=%s&user=%s&pass=%s&newpass=%s' % \
                    (self.conf['server'], self.conf['id'], urllib.quote(vals['username']), 
                     urllib.quote(vals['oldpass']), urllib.quote(vals['password1']))
 
            resp = urllib2.urlopen(url) 
            s = resp.read()
            
            val = json.loads(s)
            errstr = val.get('error')
            if errstr:
                logfile.info(errstr)
                dlg.set_warn(self.errors[val['status']])
                continue
             
            wx.MessageBox(_('Password successfully changed!'), _('Success'), wx.OK|wx.ICON_INFORMATION)
            self.conf['user'] = vals['username']
            self.conf['password'] = vals['password1']
            self.conf.dump()
            break

        dlg.Destroy()





