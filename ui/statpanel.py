# coding: utf-8
import os, sys
import wx
import  wx.html as  html
import datetime
import logfile
import drawstat

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
        tm = wx.DateTime()
        tm.Set(tday.day, tday.month, tday.year)
        self.fromdate = wx.DatePickerCtrl(self, dt=tm, size=(90, -1), 
                            style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)

        self.todate   = wx.DatePickerCtrl(self, dt=tm, size=(90, -1), 
                            style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)


        box.Add(wx.StaticText(self, -1, _('Date Start:'), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.fromdate, 0, wx.EXPAND)

        box.Add(wx.StaticText(self, -1, _("  Date End: "), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.todate, 0, wx.EXPAND)
        
        box.Add(wx.StaticText(self, -1, _("   Type "), (8, 10)), 0, wx.ALIGN_CENTER)
        #items = [_('Payout and Income'), _('Payout'), _('Income')]
        items = [_('Payout'), _('Income'), _('Surplus')]
        self.default_type = items[0]
        self.type = wx.ComboBox(self, -1, items[0], (60, 50), (80, -1), items, wx.CB_DROPDOWN)
        box.Add(self.type, 0, wx.EXPAND)
    
        box.Add(wx.StaticText(self, -1, _("   Category "), (8, 10)), 0, wx.ALIGN_CENTER)
        #items = self.data[self.default_type]
        items = [_('All Categories')]
        self.category = wx.ComboBox(self, -1, items[0], (60, 50), (100, -1), items, wx.CB_DROPDOWN)
        box.Add(self.category, 0, wx.EXPAND)

        box.Add(wx.StaticText(self, -1, u"  ", (8, 10)), 0, wx.ALIGN_CENTER)
        self.catestat = wx.Button(self, -1, _("Categroy Stat"), (20, 20)) 
        box.Add(self.catestat, 0, wx.EXPAND)
        self.monthstat = wx.Button(self, -1, _("Month Stat"), (20, 20)) 
        box.Add(self.monthstat, 0, wx.EXPAND)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box, 0, wx.EXPAND|wx.ALL, border=2)
        #self.content = html.HtmlWindow(self, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.content = wx.Panel(self)
        sizer.Add(self.content, 1, wx.EXPAND|wx.ALL)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
            
        self.Bind(wx.EVT_BUTTON, self.OnCateStatClick, self.catestat)
        self.Bind(wx.EVT_BUTTON, self.OnMonthStatClick, self.monthstat)
        self.Bind(wx.EVT_COMBOBOX, self.OnChooseType, self.type) 


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

    def OnCateStatClick(self, event):
        fromdate  = self.fromdate.GetValue()
        fromyear  = fromdate.GetYear()
        frommonth = fromdate.GetMonth()
        fromday   = fromdate.GetDay()
        
        todate  = self.todate.GetValue()
        toyear  = todate.GetYear()
        tomonth = todate.GetMonth()
        today   = todate.GetDay()

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
        sql = "select num,year,month,day,type,category from capital where year>=%d and year<=%d and month>=%d and month<=%d and day>=%d and day<=%d" % (fromyear, toyear, frommonth, tomonth, fromday, today)
        if mytype >= 0:
            sql += " and type=%d" % (mytype)

        if cate != _('All Categories'):
            cates = frame.category.cate_subs(mytype, cate)
            sql += ' and category in (%s)' % (','.join(cates))
        sql += " order by year,month,day"
        logfile.info('stat:', sql)
        rets = frame.db.query(sql)
       
        print 'rets:', rets

        if rets:
            catevals = {}
            for row in rets:
                cate = row['category'] 
                pcate = frame.category.parent_cate_name(row['type'], cate) 
                if not pcate:
                    pcate = frame.category.catemap(row['type'], cate)

                if catevals.has_key(pcate):
                    catevals[pcate] += row['num']
                else:
                    catevals[pcate] = row['num']

            
            data = []
            for k in catevals:
                data.append({'data':catevals[k], 'name':k})
            
            print 'content data:', data
            self.content = drawstat.ChartPie(self, data)
            self.Refresh()
            


    def OnMonthStatClick(self, event):
        pass


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

 








        
