# coding: utf-8
import os, sys
import wx
import  wx.html as  html
import datetime
import logfile

class StatPanel (wx.Panel):
    def __init__(self, parent, readydata):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.data = readydata
        
        for k in self.data:
            self.data[k].insert(0, _('All Categories'))        

        box = wx.BoxSizer(wx.HORIZONTAL)
        tday = datetime.date.today()
        items = [ str(x) for x in range(2009, 2020) ]
        self.fromyear  = wx.ComboBox(self, -1, str(tday.year), (60, 50), (60, -1), items, wx.CB_DROPDOWN)
        self.toyear  = wx.ComboBox(self, 500, str(tday.year), (60, 50), (60, -1), items, wx.CB_DROPDOWN)
        items = [ str(x) for x in range(1, 13) ]
        self.frommonth = wx.ComboBox(self, -1, str(tday.month), (60, 50), (60, -1), items, wx.CB_DROPDOWN)
        self.tomonth = wx.ComboBox(self, -1, str(tday.month), (60, 50), (60, -1), items, wx.CB_DROPDOWN)

        box.Add(wx.StaticText(self, -1, _('Date Start:'), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.fromyear, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, _(" Year "), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.frommonth, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, _(" Month "), (8, 10)), 0, wx.ALIGN_CENTER)

        box.Add(wx.StaticText(self, -1, _("  Date End: "), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.toyear, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, _(" Year "), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.tomonth, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, _(" Month "), (8, 10)), 0, wx.ALIGN_CENTER)
        
        box.Add(wx.StaticText(self, -1, _("   Type "), (8, 10)), 0, wx.ALIGN_CENTER)
        items = [_('Payout'), _('Income')]
        self.default_type = items[0]
        self.type = wx.ComboBox(self, -1, items[0], (60, 50), (60, -1), items, wx.CB_DROPDOWN)
        box.Add(self.type, 0, wx.EXPAND)
    
        box.Add(wx.StaticText(self, -1, _("   Category "), (8, 10)), 0, wx.ALIGN_CENTER)
        items = self.data[self.default_type]
        self.category = wx.ComboBox(self, -1, items[0], (60, 50), (100, -1), items, wx.CB_DROPDOWN)
        box.Add(self.category, 0, wx.EXPAND)

        box.Add(wx.StaticText(self, -1, u"    ", (8, 10)), 0, wx.ALIGN_CENTER)
        self.go = wx.Button(self, -1, _("Statistic!"), (20, 20)) 
        box.Add(self.go, 0, wx.EXPAND)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box, 0, wx.EXPAND|wx.ALL, border=2)
        self.content = html.HtmlWindow(self, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        sizer.Add(self.content, 1, wx.EXPAND|wx.ALL)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
            
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.go)
        self.Bind(wx.EVT_COMBOBOX, self.OnChooseType, self.type) 

    def OnClick(self, event):
        fromyear  = self.fromyear.GetValue()
        toyear    = self.toyear.GetValue()
        frommonth = self.frommonth.GetValue()
        tomonth   = self.tomonth.GetValue()
        type      = self.type.GetValue()
        cate      = self.category.GetValue()
        
        if type == _('Payout'):
            mytype = 0
        else:
            mytype = 1

        sql = "select num,year,month from capital where type=%d and year>=%s and year<=%s and month>=%s and month<=%s" % (mytype, fromyear, toyear, frommonth, tomonth)
        if cate != _('All Categories'):
            sql += ' and category=%d' % (self.parent.parent.category.catemap(mytype, cate))
        sql += " order by year,month"
        logfile.info('stat:', sql)
        rets = self.parent.parent.db.query(sql)
        
        if rets:
            result = {}
            for item in range(int(fromyear), int(toyear)+1):
                result[item] = [ 0 for x in range(0,13) ]

            for row in rets:
                item = result[row['year']]
                item[row['month']] += row['num']

            for k in result:
                item = result[k]
                item[0] = sum(item)
            keys = result.keys()
            keys.sort()
            s = '<center><table border=1 width="95%"><tr><td width=60></td>'
            for k in keys:
                s += u"<td>%d</td>" % (k)
            s += "</tr>"
           
            for rowi in range(1, 13):
                s += u"<tr><td>%d%s</td>" % (rowi, _('Month'))
                for k in keys:
                    item = result[k]
                    s += "<td>%.2f</td>" % (item[rowi])
                s += "</tr>"

            s += u"<tr><td>%s</td>" % (_('Sum'))
            for k in keys:
                item = result[k]
                s += "<td>%.2f</td>" % (item[0])

            s += "</tr></table></center>"

            self.content.SetPage(s)

    def OnChooseType(self, event):
        val = self.type.GetValue()
        self.default_type = val
        self.category.Clear()

        for x in self.data[val]:
            self.category.Append(x)
        
        self.category.SetValue(self.data[val][0])

 








        
