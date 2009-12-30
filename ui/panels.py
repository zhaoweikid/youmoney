# coding: utf-8
import os, sys
import datetime
import wx
import wx.lib.sized_controls as sc
import wx.gizmos as gizmos
import logfile

class CategoryPanel (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=0)
        self.parent= parent        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.tree = gizmos.TreeListCtrl(self, -1, style=wx.TR_DEFAULT_STYLE|
                    wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_HIDE_ROOT)
        sizer.Add(self.tree, 1, wx.EXPAND|wx.ALL)
        
        self.init()

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated, self.tree)

    def init(self):
        self.tree.AddColumn(u'分类')
        self.tree.AddColumn(u'本月总计')

        self.tree.SetMainColumn(0)
        self.tree.SetColumnWidth(0, 200)
        
    def load(self, cate):
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot("Root")
        self.tree.SetItemText(self.root, "1", 1)
        self.tree.SetPyData(self.root, None)

        for root in [cate.payout_tree, cate.income_tree]:
            child = self.tree.AppendItem(self.root, root.name)
            self.tree.SetItemText(child, str(root.num), 1)
            self.tree.SetPyData(child, {'id':root.id})
            
            for ch in root.childs: 
                c1 = self.tree.AppendItem(child, ch.name)
                self.tree.SetItemText(c1, str(ch.num), 1)
                self.tree.SetPyData(c1, {'id':ch.id})
                for ch2 in ch.childs:
                    c2 = self.tree.AppendItem(c1, ch2.name)
                    self.tree.SetItemText(c2, str(ch2.num), 1)
                    self.tree.SetPyData(c2, {'id':ch2.id})
 
        self.tree.ExpandAll(self.root)

    def OnItemActivated(self, event):
        data = self.tree.GetPyData(event.GetItem())
        frame = self.parent.parent
        if data['id'] > 0:
            sql = "select * from category where id=" + str(data['id'])
            ret = frame.db.query(sql)
            if ret:
                row = ret[0]
                if row['parent'] > 0:
                    upcate = frame.category.catemap(row['type'], row['parent'])
                else:
                    upcate = u'无上级分类'
                if row['type'] == 0:
                    ct = u'支出'
                else:
                    ct = u'收入'
                ready = {'cates':[], 'cate':row['name'], 'upcate':upcate, 'catetype':ct, 'mode':'update', 'id':row['id']}

                frame.cateedit_dialog(ready)


class PayoutListPanel (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=0)
        self.parent = parent

        box = wx.BoxSizer(wx.HORIZONTAL)
        tday = datetime.date.today()
        items = [ str(x) for x in range(2009, 2020) ]
        self.year  = wx.ComboBox(self, 500, str(tday.year), (60, 50), (60, -1), items, wx.CB_DROPDOWN)
        items = [ str(x) for x in range(1, 13) ]
        self.month = wx.ComboBox(self, 500, str(tday.month), (60, 50), (60, -1), items, wx.CB_DROPDOWN)
        box.Add(wx.StaticText(self, -1, u"日期: ", (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.year, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, u" 年 ", (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.month, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, u" 月", (8, 10)), 0, wx.ALIGN_CENTER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box, 0, wx.EXPAND|wx.ALL, border=2)
        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        sizer.Add(self.list, 1, wx.EXPAND|wx.ALL)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_COMBOBOX, self.OnChooseYear, self.year)
        self.Bind(wx.EVT_COMBOBOX, self.OnChooseMonth, self.month)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)

        #self.init()
        self.load()
    
    def init(self):
        self.list.InsertColumn(0, u"日期")
        self.list.InsertColumn(1, u"分类")
        self.list.InsertColumn(2, u"金额")
        self.list.InsertColumn(3, u"支付方式")


    def load(self):
        self.list.ClearAll()
        self.init()

        year  = self.year.GetValue()
        month = self.month.GetValue()

        sql = "select * from capital where year=%s and month=%s and type=0 order by id" % (year, month)
        logfile.info(sql)
        rets = self.parent.parent.db.query(sql)
        logfile.info('list:', rets)
        if rets:
            for row in rets:
                mytime = '%d-%02d-%02d' % (row['year'], row['month'], row['day'])
                item = self.list.InsertStringItem(0, mytime)
                cate = self.parent.parent.category.payout_catemap[row['category']]
                self.list.SetStringItem(item, 1, cate)
                self.list.SetStringItem(item, 2, str(row['num']))
                self.list.SetItemData(item, row['id'])
                if row['payway'] == 1:
                    payway = u'现金'
                else:
                    payway = u'信用卡'
                self.list.SetStringItem(item, 3, payway)
       

    def OnChooseYear(self, event):
        self.load()

    def OnChooseMonth(self, event):
        self.load()

    
    def OnItemActivated(self, event):
        currentItem = event.m_itemIndex
        id = self.list.GetItemData(currentItem)
        category = self.parent.parent.category
        sql = "select * from capital where id=" + str(id)
        ret = self.parent.parent.db.query(sql)
        if ret:
            row = ret[0]
            if row['payway'] == 1:
                payway = u'现金'
            else:
                payway = u'信用卡'

            ready = {'cates':category.payout_catelist, 
                     'cate':category.catestr_by_id('payout', row['category']), 'num': row['num'], 
                     'explain':row['explain'], 
                     'year':row['year'], 'month':row['month'], 'day':row['day'], 
                     'pay':payway, 'mode':'update', 'id':row['id']}

            logfile.info('ready:', ready)
            self.parent.parent.payout_dialog(ready)


class ContentTab (wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, -1, size=(21,21), style=wx.BK_DEFAULT)
        self.parent = parent
        self.cate = CategoryPanel(self)
        self.AddPage(self.cate, u"分类")
        self.payoutlist = PayoutListPanel(self)
        self.AddPage(self.payoutlist, u"支出列表")


    def load_category(self, cate):
        self.cate.load(cate)
    

    def load_payout(self):
        self.payoutlist.load()
