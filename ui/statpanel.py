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
        self.fromyear  = wx.ComboBox(self, -1, str(tday.year), (60, 50), (70, -1), items, wx.CB_DROPDOWN)
        self.toyear  = wx.ComboBox(self, 500, str(tday.year), (60, 50), (70, -1), items, wx.CB_DROPDOWN)
        items = [ str(x) for x in range(1, 13) ]
        #self.frommonth = wx.ComboBox(self, -1, str(tday.month), (60, 50), (60, -1), items, wx.CB_DROPDOWN)
        #self.tomonth = wx.ComboBox(self, -1, str(tday.month), (60, 50), (60, -1), items, wx.CB_DROPDOWN)

        box.Add(wx.StaticText(self, -1, _('Date Start:'), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.fromyear, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, _(" Year "), (8, 10)), 0, wx.ALIGN_CENTER)
        #box.Add(self.frommonth, 0, wx.EXPAND)
        #box.Add(wx.StaticText(self, -1, _(" Month "), (8, 10)), 0, wx.ALIGN_CENTER)

        box.Add(wx.StaticText(self, -1, _("  Date End: "), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.toyear, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, _(" Year "), (8, 10)), 0, wx.ALIGN_CENTER)
        #box.Add(self.tomonth, 0, wx.EXPAND)
        #box.Add(wx.StaticText(self, -1, _(" Month "), (8, 10)), 0, wx.ALIGN_CENTER)
        
        box.Add(wx.StaticText(self, -1, _("   Type "), (8, 10)), 0, wx.ALIGN_CENTER)
        items = [_('Payout and Income'), _('Payout'), _('Income')]
        self.default_type = items[0]
        self.type = wx.ComboBox(self, -1, items[0], (60, 50), (100, -1), items, wx.CB_DROPDOWN)
        box.Add(self.type, 0, wx.EXPAND)
    
        box.Add(wx.StaticText(self, -1, _("   Category "), (8, 10)), 0, wx.ALIGN_CENTER)
        #items = self.data[self.default_type]
        items = [_('All Categories')]
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


    def create_html_one(self, fromyear, toyear, data):
        result = {}
        for item in range(int(fromyear), int(toyear)+1):
            # payout, income
            result[item] = [[ 0 for x in range(0,13) ], [ 0 for x in range(0,13) ]]
    
        mytype = None
        for row in data:
            item = result[row['year']]
            mytype = row['type']
            item[mytype][row['month']] += row['num']

        for k in result:
            item = result[k]
            item[0][0] = sum(item[0])
            item[1][0] = sum(item[1])

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
                s += "<td>%.2f</td>" % (item[mytype][rowi])
            s += "</tr>"

        s += u"<tr><td>%s</td>" % (_('Sum'))
        for k in keys:
            item = result[k]
            s += "<td>%.2f</td>" % (item[mytype][0])
            
        s += "</tr></table></center>"

        return s


    def create_html_both(self, fromyear, toyear, data):
        result = {}
        for item in range(int(fromyear), int(toyear)+1):
            # payout, income
            result[item] = [[ 0 for x in range(0,13) ], [ 0 for x in range(0,13) ]]

        for row in data:
            item = result[row['year']]
            item[row['type']][row['month']] += row['num']

        for k in result:
            item = result[k]
            item[0][0] = sum(item[0])
            item[1][0] = sum(item[1])

        keys = result.keys()
        keys.sort()
        s = '<center><table border=1 width="95%"><tr><td width=60></td>'
        for k in keys:
            s += u"<td>%d <br>%s/%s</td>" % (k, _('Payout'), _('Income'))
        s += "</tr>"
           
        for rowi in range(1, 13):
            s += u"<tr><td>%d%s</td>" % (rowi, _('Month'))
            for k in keys:
                item = result[k]
                s += "<td>%.2f/%.2f</td>" % (item[0][rowi], item[1][rowi])
            s += "</tr>"

        s += u"<tr><td>%s</td>" % (_('Sum'))
        for k in keys:
            item = result[k]
            s += "<td>%.2f/%.2f</td>" % (item[0][0], item[1][0])
            
        s += u"</tr><tr><td>%s</td>" % (_('Balance'))
        for k in keys:
            item = result[k]
            s += "<td>%.2f</td>" % (item[1][0] - item[0][0])

        s += "</tr></table></center>"

        return s


    def OnClick(self, event):
        fromyear  = self.fromyear.GetValue()
        toyear    = self.toyear.GetValue()
        type      = self.type.GetValue()
        cate      = self.category.GetValue()

        frame = self.parent.parent
        
        if type == _('Payout'):
            mytype = 0
        elif type == _('Income'):
            mytype = 1
        else:
            mytype = -1

        #sql = "select num,year,month from capital where type=%d and year>=%s and year<=%s" % (mytype, fromyear, toyear)
        sql = "select num,year,month,type from capital where year>=%s and year<=%s" % (fromyear, toyear)
        if mytype >= 0:
            sql += " and type=%d" % (mytype)

        if cate != _('All Categories'):
            cates = frame.category.cate_subs(mytype, cate)
            sql += ' and category in (%s)' % (','.join(cates))
        sql += " order by year,month"
        logfile.info('stat:', sql)
        rets = frame.db.query(sql)
        
        if rets:
            if mytype == -1:
                self.content.SetPage(self.create_html_both(fromyear, toyear, rets))
            else:
                self.content.SetPage(self.create_html_one(fromyear, toyear, rets))
        else:
            self.content.SetPage(_('No data'))

    def OnChooseType(self, event):
        val = self.type.GetValue()
        self.default_type = val
        self.category.Clear()
        
        logfile.info('Choose type:', val)

        if val == _('Payout and Income'):
            self.category.Append(_('All Categories'))
            self.category.SetValue(_('All Categories'))
        else:
            for x in self.data[val]:
                self.category.Append(x)
        
            self.category.SetValue(self.data[val][0])

 








        
