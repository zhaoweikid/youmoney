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
        tm.Set(tday.day, tday.month-1, tday.year)
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
        self.content = drawstat.CharDrawer(self)
        self.content.SetBackgroundColour(wx.WHITE)
        sizer.Add(self.content, 1, wx.EXPAND|wx.ALL)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
            
        self.Bind(wx.EVT_BUTTON, self.OnCateStatClick, self.catestat)
        self.Bind(wx.EVT_BUTTON, self.OnMonthStatClick, self.monthstat)
        self.Bind(wx.EVT_COMBOBOX, self.OnChooseType, self.type) 


    def query_input(self, qtype='category'):
        fromdate  = self.fromdate.GetValue()
        fromyear  = fromdate.GetYear()
        frommonth = fromdate.GetMonth() + 1
        fromday   = fromdate.GetDay()
        
        todate  = self.todate.GetValue()
        toyear  = todate.GetYear()
        tomonth = todate.GetMonth() + 1
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
        
        if frommonth > tomonth:
            maxmonth = frommonth
            minmonth = tomonth
        else:
            maxmonth = tomonth
            minmonth = frommonth
        
        endsql = ''

        if mytype >= 0:
            endsql += " and type=%d" % (mytype)

        if cate != _('All Categories'):
            cates = frame.category.cate_subs(mytype, cate)
            endsql += ' and category in (%s)' % (','.join(cates))
        #endsql += " order by year,month,day"

        #sql = "select num,year,month from capital where type=%d and year>=%s and year<=%s" % (mytype, fromyear, toyear)
        if qtype == 'category':
            if fromyear == toyear and frommonth == tomonth:
                #sql = "select num,year,month,day,type,category from capital where year>=%d and year<=%d and month>=%d and month<=%d and day>=%d and day<=%d %s" % (fromyear, toyear, minmonth, maxmonth, fromday, today, endsql)
                sql = "select num,year,month,day,type,category from capital where year=%d and month=%d and day>=%d and day<=%d %s order by year,month,day" % (fromyear, frommonth, fromday, today, endsql)
            else:
                years = range(fromyear, toyear+1)
                sqls = []
                sql = "select num,year,month,day,type,category from capital where year=%d and month=%d and day>=%d %s" % (fromyear, frommonth, fromday, endsql)
                sqls.append(sql)
                
                if len(years) <= 1:
                    sql = "select num,year,month,day,type,category from capital where year>=%d and year<=%d and month>%d and month<%d %s" % (fromyear, toyear, minmonth, maxmonth, endsql)
                    sqls.append(sql)
                else:
                    sql = "select num,year,month,day,type,category from capital where year=%d and month>%d  %s" % (fromyear, frommonth, endsql)
                    sqls.append(sql)
                    sql = "select num,year,month,day,type,category from capital where year=%d and month<%d  %s" % (toyear, tomonth, endsql)
                    sqls.append(sql)

                    sql = "select num,year,month,day,type,category from capital where year>=%d and year<=%d %s" % (fromyear, toyear, endsql)
                    sqls.append(sql)

                     
                sql = "select num,year,month,day,type,category from capital where year=%d and month=%d and day<=%d %s" % (toyear, tomonth, today, endsql)
                sqls.append(sql)

                sql = ' union '.join(sqls) + ' order by year,month,day'
 
        elif qtype == 'month':
            years = range(fromyear, toyear+1)
            if len(years) <= 1:
                sql = "select num,year,month,day,type,category from capital where year>=%d and year<=%d and month>=%d and month<=%d %s" % (fromyear, toyear, minmonth, maxmonth, endsql)
            else:
                sqls = []
                sql = "select num,year,month,day,type,category from capital where year=%d and month>=%d %s" % (fromyear, frommonth, endsql)
                sqls.append(sql)
                for ye in years[1:-1]:
                    sql = "select num,year,month,day,type,category from capital where year>%d and year<%d %s" % (fromyear, toyear, endsql)
                    sqls.append(sql)

                sql = "select num,year,month,day,type,category from capital where year=%d and month<=%d %s" % (toyear, tomonth, endsql)
                sqls.append(sql)

                sql = ' union '.join(sqls) + ' order by year,month,day'


        logfile.info('stat:', sql)
        rets = frame.db.query(sql)
        
        print sql

        return rets

    def OnCateStatClick(self, event):
        frame = self.parent.parent
        rets = self.query_input('category')
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
            self.content.draw_pie(data)

    def OnMonthStatClick(self, event):
        frame = self.parent.parent
        rets = self.query_input('month')
        print 'rets:', rets

        if rets:
            vals = {}
            for row in rets:
                key = '%d%02d' % (row['year'], row['month'])
                print key
                if vals.has_key(key):
                    vals[key] += row['num']
                else:
                    vals[key] = row['num']
            keys = vals.keys()
            keys.sort()

            data = []
            for k in keys:
                data.append({'data':int(vals[k]), 'name':k[4:]+u'月'})
            
            print 'content data:', data
            self.content.draw_bar(data)

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

 








        
