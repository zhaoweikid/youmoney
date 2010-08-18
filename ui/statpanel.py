# coding: utf-8
import os, sys
import wx
import wx.html as  html
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
        tmto = wx.DateTime()
        tmto.Set(tday.day, tday.month-1, tday.year)
        tmfrom = wx.DateTime()
        tmfrom.Set(1, tday.month-1, tday.year)
        self.fromdate = wx.DatePickerCtrl(self, dt=tmfrom, size=(90, -1), 
                            style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)

        self.todate   = wx.DatePickerCtrl(self, dt=tmto, size=(90, -1), 
                            style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)


        box.Add(wx.StaticText(self, -1, _('Date Start:'), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.fromdate, 0, wx.EXPAND)

        box.Add(wx.StaticText(self, -1, _("  Date End: "), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.todate, 0, wx.EXPAND)
        
        box.Add(wx.StaticText(self, -1, _("   Type "), (8, 10)), 0, wx.ALIGN_CENTER)
        #items = [_('Payout and Income'), _('Payout'), _('Income')]
        #items = [_('Payout'), _('Income'), _('Surplus')]
        items = [_('Payout'), _('Income')]
        self.default_type = items[0]
        self.type = wx.ComboBox(self, -1, items[0], (60, 50), (80, -1), items, wx.CB_DROPDOWN|wx.CB_READONLY)
        box.Add(self.type, 0, wx.EXPAND)
    
        box.Add(wx.StaticText(self, -1, _("   Category "), (8, 10)), 0, wx.ALIGN_CENTER)
        #items = self.data[self.default_type]
        #items = [_('All Categories')]
        items = self.data[_('Payout')]
        self.category = wx.ComboBox(self, -1, items[0], (60, 50), (100, -1), items, wx.CB_DROPDOWN|wx.CB_READONLY)
        box.Add(self.category, 0, wx.EXPAND)

        box.Add(wx.StaticText(self, -1, u"  ", (8, 10)), 0, wx.ALIGN_CENTER)
        self.catestat = wx.Button(self, -1, _("Categroy Stat"), (20, 20)) 
        box.Add(self.catestat, 0, wx.EXPAND)
        self.monthstat = wx.Button(self, -1, _("Month Stat"), (20, 20)) 
        box.Add(self.monthstat, 0, wx.EXPAND)
        self.tablestat = wx.Button(self, -1, _("Table Stat"), (20, 20)) 
        box.Add(self.tablestat, 0, wx.EXPAND)
 
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
        self.Bind(wx.EVT_BUTTON, self.OnTableStatClick, self.tablestat)
        self.Bind(wx.EVT_COMBOBOX, self.OnChooseType, self.type) 

    def reload_category(self, cates):
        self.data = cates
        for k in self.data:
            self.data[k].insert(0, _('All Categories'))        

        self.choose_type()


    def query_input(self, qtype='category'):
        fromdate  = self.fromdate.GetValue()
        fromyear  = fromdate.GetYear()
        frommonth = fromdate.GetMonth() + 1
        fromday   = fromdate.GetDay()
        
        todate  = self.todate.GetValue()
        toyear  = todate.GetYear()
        tomonth = todate.GetMonth() + 1
        today   = todate.GetDay()

        type    = self.type.GetValue()
        cate    = self.category.GetValue()
        
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
        #if mytype >= 0:
        #    endsql += " and type=%d" % (mytype)

        if cate != _('All Categories'):
            logfile.info("cate:", cate)
            cates = frame.category.cate_subs_id(mytype, cate)
            logfile.info("cates:", cates)
            cates = map(str, cates)
            endsql += ' and category in (%s)' % (','.join(cates))
        #endsql += " order by year,month,day"
        
        prefixsql = 'select num,year,month,day,type,category from capital '
        #sql = "select num,year,month from capital where type=%d and year>=%s and year<=%s" % (mytype, fromyear, toyear)
        if qtype == 'category':
            #if cate != _('All Categories'):
            #    return [], (), ()

            if fromyear == toyear and frommonth == tomonth:
                #sql = "select num,year,month,day,type,category from capital where year>=%d and year<=%d and month>=%d and month<=%d and day>=%d and day<=%d %s" % (fromyear, toyear, minmonth, maxmonth, fromday, today, endsql)
                sql = prefixsql + "where year=%d and month=%d and day>=%d and day<=%d %s order by year,month,day" % (fromyear, frommonth, fromday, today, endsql)
            else:
                years = range(fromyear, toyear+1)
                sqls = []
                sql = prefixsql + "where year=%d and month=%d and day>=%d %s" % (fromyear, frommonth, fromday, endsql)
                sqls.append(sql)
                
                if len(years) <= 1: # one year, multip month, entire months
                    sql = prefixsql + "where year>=%d and year<=%d and month>%d and month<%d %s" % (fromyear, toyear, minmonth, maxmonth, endsql)
                    sqls.append(sql)
                else: # multip year
                    sql = prefixsql + "where year=%d and month>%d %s" % (fromyear, frommonth, endsql)
                    sqls.append(sql)
                    sql = prefixsql + "where year=%d and month<%d %s" % (toyear, tomonth, endsql)
                    sqls.append(sql)

                    sql = prefixsql + "where year>%d and year<%d %s" % (fromyear, toyear, endsql)
                    sqls.append(sql)
                     
                sql = prefixsql + "where year=%d and month=%d and day<=%d %s" % (toyear, tomonth, today, endsql)
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
        if not rets:
            rets = []
        return rets, (fromyear, frommonth), (toyear, tomonth)

    def OnCateStatClick(self, event):
        type  = self.type.GetValue()
        icate = self.category.GetValue()
        
        if type == _('Payout'):
            mytype = 0
        elif type == _('Income'):
            mytype = 1
        else:
            mytype = -1
 
        if mytype == -1:
            rets = []
        else:
            frame = self.parent.parent
            rets, fromdate, todate = self.query_input('category')
        surplus_val = 0
        catevals = {}
        for row in rets:
            if row['type'] == 1:
                surplus_val += row['num']
            else:
                surplus_val -= row['num']

            if row['type'] != mytype:
                continue

            cate = row['category'] 

            if icate == _('All Categories'):
                pcate = frame.category.parent_cate_name(row['type'], cate) 
                if not pcate:
                    pcate = frame.category.catemap(row['type'], cate)
            else:
                pcate = frame.category.catemap(row['type'], cate)
                

            if catevals.has_key(pcate):
                catevals[pcate] += row['num']
            else:
                catevals[pcate] = row['num']

        data = []
        for k in catevals:
            data.append({'data':catevals[k], 'name':k})
        
        logfile.info('data:', data, 'surplus_val:', surplus_val)    
        self.content.draw_pie(data, surplus_val)

    def OnMonthStatClick(self, event):
        data = self.statdata()
        self.content.draw_bar(data)

    def OnTableStatClick(self, event):
        cate = self.category.GetValue()
        issubcate = False
        if cate != _('All Categories'):
            issubcate = True

        vals = self.statdata()
        
        # [[year, [month, [income_vals, payout_vals, surplus_vals]]], ]
        data = []
        lastyear = 0
        sums = None
        for i in range(0, len(vals[0])):
            k = vals[0][i][0]
            year  = k[:4]
            month = k[4:]

            inc = int(vals[0][i][1])
            pay = int(vals[1][i][1])
            if not issubcate:
                sur = int(vals[2][i][1])
            else:
                sur = 0
 
            if year == lastyear:
                data[-1][1].append([int(month), [inc, pay, sur]])
                sums[0] += inc
                sums[1] += pay
                sums[2] += sur
            else:
                sums = [inc, pay, sur]
                data.append([int(year), [[int(month), [inc, pay, sur]]], sums])
            lastyear = year

        #pprint.pprint(data)
        self.content.draw_table(data)

    def statdata(self):
        cate = self.category.GetValue()
        issubcate = False
        if cate != _('All Categories'):
            issubcate = True

        type  = self.type.GetValue()
        frame = self.parent.parent
        rets, fromdate, todate = self.query_input('month')
        
        # payout vals, income vals, surplus vals
        vals = [{}, {}, {}]
        keys = []
        for ye in range(fromdate[0], todate[0]+1):
            if ye == fromdate[0]:
                bm = fromdate[1]
            else:
                bm = 1
            if ye == todate[0]:
                em = todate[1]
            else:
                em = 12
            for mo in range(bm, em+1):
                k = '%d%02d' % (ye, mo)
                keys.append(k)
                vals[0][k] = 0
                vals[1][k] = 0
                vals[2][k] = 0
       
        for row in rets:
            key = '%d%02d' % (row['year'], row['month'])
            vals[row['type']][key] += row['num']
        
        if not issubcate:
            for k in vals[2]:
                vals[2][k] = vals[1][k] - vals[0][k]

        data = [[], [], []]
        for i in range(0, len(data)):
            for k in keys:
                data[i].append([k, vals[i][k]])

        swap = data[0]
        data[0] = data[1]
        data[1] = swap
        
        return data

    def OnChooseType(self, event):
        self.choose_type()

    def choose_type(self):
        val = self.type.GetValue()
        self.default_type = val
        self.category.Clear()

        logfile.info('Choose type:', val)

        if val == _('Surplus'):
            self.category.Append(_('All Categories'))
            self.category.SetValue(_('All Categories'))
        else:
            for x in self.data[val]:
                self.category.Append(x)
        
            self.category.SetValue(self.data[val][0])

 








        
