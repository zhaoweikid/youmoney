# coding: utf-8
import os, sys
import datetime, copy, types
import pprint
import wx
import wx.lib.sized_controls as sc
import wx.gizmos as gizmos
import logfile, statpanel, storage

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
        
        self.currentItem = None

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated, self.tree)
        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnPopupMenu) 
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnItemSelected, self.tree)

    def init(self):
        self.tree.AddColumn(_("Category"))
        self.tree.AddColumn(_("Month Total"))
        self.tree.AddColumn(_("Day Total"))

        self.tree.SetMainColumn(0)
        self.tree.SetColumnWidth(0, 200)
       
    def get_all_children(self, parent):
        ret = []
        child,cookie = self.tree.GetFirstChild(parent)
        if not child:
            return ret
        ret.append(child)
        while True:
            other, cookie = self.tree.GetNextChild(parent, cookie)
            if not other:
                return ret
            ret.append(other)
    
    def load(self, cate):
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot("Root")
        self.tree.SetItemText(self.root, "1", 1)
        self.tree.SetPyData(self.root, None)

        for root in [cate.payout_tree, cate.income_tree]:
            child = self.tree.AppendItem(self.root, root.name)
            self.tree.SetItemText(child, str(root.month_num), 1)
            self.tree.SetItemText(child, str(root.day_num), 2)
            self.tree.SetPyData(child, {'id':root.id})
            
            for ch in root.childs: 
                c1 = self.tree.AppendItem(child, ch.name)
                self.tree.SetItemText(c1, str(ch.month_num), 1)
                self.tree.SetItemText(c1, str(ch.day_num), 2)
                self.tree.SetPyData(c1, {'id':ch.id})
                for ch2 in ch.childs:
                    c2 = self.tree.AppendItem(c1, ch2.name)
                    self.tree.SetItemText(c2, str(ch2.month_num), 1)
                    self.tree.SetItemText(c2, str(ch2.day_num), 2)
                    self.tree.SetPyData(c2, {'id':ch2.id})
 
        #self.tree.ExpandAll(self.root)
        self.tree.Expand(self.root)
        for x in self.get_all_children(self.root):
            self.tree.Expand(x)

    def OnPopupMenu(self, event):
        pt = event.GetPosition();
        test = self.tree.HitTest(pt)
        if test[0]:
            self.tree.SelectItem(test[0])
        
        if not hasattr(self, "ID_POPUP_DEL"):
            self.ID_POPUP_DEL = wx.NewId()
            self.ID_POPUP_EDIT = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnCategoryDel, id=self.ID_POPUP_DEL)
            self.Bind(wx.EVT_MENU, self.OnItemActivated, id=self.ID_POPUP_EDIT)
        menu = wx.Menu()
        menu.Append(self.ID_POPUP_EDIT, _('Edit')) 
        menu.Append(self.ID_POPUP_DEL, _('Delete')) 
        self.PopupMenu(menu)
        menu.Destroy()


    def OnItemActivated(self, event):
        try:
            data  = self.tree.GetPyData(event.GetItem())
        except:
            data  = self.tree.GetPyData(self.currentItem)

        frame = self.parent.parent
        if data['id'] > 0:
            sql = "select * from category where id=" + str(data['id'])
            ret = frame.db.query(sql)
            if ret:
                row = ret[0]
                if row['parent'] > 0:
                    upcate = frame.category.catemap(row['type'], row['parent'])
                else:
                    upcate = _("No Higher Category")
                if row['type'] == 0:
                    ct = _('Payout')
                else:
                    ct = _('Income')
                ready = {'cates':[], 'cate':row['name'], 'upcate':upcate, 'catetype':ct, 'mode':'update', 'id':row['id']}

                frame.cateedit_dialog(ready)

    def OnCategoryDel(self, event):
        data  = self.tree.GetPyData(self.currentItem)
        if not data or data['id'] <= 0:
            logfile.info("category data invalid.")
            return
        frame = self.parent.parent
 
        sql = "select * from category where id=" + str(data['id'])
        ret = frame.db.query(sql)
        if not ret:
            logfile.info('not found del category:', data['id'])
            return
        mytype = ret[0]['type']
        name   = ret[0]['name']
        
        if name == _('No Category'):
            dlg = wx.MessageDialog(self, _('Can not delete this category!'),
                               _('Notice:'),
                               wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   
        else:
            dlg = wx.MessageDialog(self, _('To delete category') + '"' + name + '"' + _(', all child categories will move to "No Category"'),
                               _('Notice:'),
                               wx.OK | wx.ICON_INFORMATION | wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            # 检查要删除的所有分类，包括子类
            idlist = [str(data['id'])]
            sql = "select * from category where parent=" + str(data['id'])
            ret = frame.db.query(sql)
            if ret:
                for row in ret:
                    idlist.append(str(row['id']))
            ids = ','.join(idlist)
            # 检查是否有 未分类
            sql = u"select * from category where name='%s' and type=%d" %(_('No Category'), mytype)
            ret = frame.db.query(sql)
            if not ret:
                sql = "insert into category (name,parent,type) values ('%s',0,%d)" % (_('No Category'), mytype)
                frame.db.execute(sql)
                sql = u"select * from category where name='%s' and type=%d" % (_('No Category'), mytype)

                ret = frame.db.query(sql)
 
            mycid = ret[0]['id']

            # 更新
            try:
                sql = "update capital set category=%d where category in (%s) and type=%d" % (mycid, ids, mytype)
                logfile.info('update category:', sql)
                frame.db.execute(sql, False)

                sql = "update recycle set category=%d where category in (%s) and type=%d" % (mycid, ids, mytype)
                logfile.info('update recycle:', sql)
                frame.db.execute(sql, False)
 
                sql = "delete from category where id=%d or parent=%d" % (data['id'], data['id'])
                frame.db.execute(sql, False)
            except Exception, e:
                frame.db.rollback()
                wx.MessageBox(_('Delete category failure!') + str(e), _('Delete category information'), wx.OK|wx.ICON_INFORMATION)
            else:
                frame.db.commit()
            frame.reload()
        dlg.Destroy()
    
    def OnItemSelected(self, event):
        self.currentItem = event.GetItem()

class ItemListPanel (wx.Panel):
    type = "payout"
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=0)
        self.parent = parent

        box = wx.BoxSizer(wx.HORIZONTAL)
        tday = datetime.date.today()
        items = [ str(x) for x in range(2009, 2020) ]
        self.year  = wx.ComboBox(self, 500, str(tday.year), (60, 50), (80, -1), items, wx.CB_DROPDOWN|wx.CB_READONLY)
        items = [ str(x) for x in range(1, 13) ]
        self.month = wx.ComboBox(self, 500, str(tday.month), (60, 50), (60, -1), items, wx.CB_DROPDOWN|wx.CB_READONLY)
        box.Add(wx.StaticText(self, -1, _(' Date: '), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.year, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, _(" Year: "), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(self.month, 0, wx.EXPAND)
        box.Add(wx.StaticText(self, -1, _(" Month:"), (8, 10)), 0, wx.ALIGN_CENTER)
        box.Add(wx.StaticText(self, -1, _("  Sum: "), (8, 10)), 0, wx.ALIGN_CENTER)
        self.total = wx.TextCtrl(self, -1, size=(100,-1), style=wx.TE_READONLY)
        box.Add(self.total, 0, wx.ALIGN_CENTER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box, 0, wx.EXPAND|wx.ALL, border=2)
        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        sizer.Add(self.list, 1, wx.EXPAND|wx.ALL)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        self.currentItem = None
        self.Bind(wx.EVT_COMBOBOX, self.OnChooseYear, self.year)
        self.Bind(wx.EVT_COMBOBOX, self.OnChooseMonth, self.month)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnPopupMenu) 
        #self.init()
        self.load()
   
    def OnPopupMenu(self, event):
        if not hasattr(self, "ID_POPUP_DEL"):
            self.ID_POPUP_DEL = wx.NewId()
            self.ID_POPUP_EDIT = wx.NewId()
            
            self.Bind(wx.EVT_MENU, self.OnDelete, id=self.ID_POPUP_DEL)
            self.Bind(wx.EVT_MENU, self.OnItemActivated, id=self.ID_POPUP_EDIT)
        menu = wx.Menu()
        menu.Append(self.ID_POPUP_EDIT, _("Edit"))
        menu.Append(self.ID_POPUP_DEL, _("Delete"))
        self.PopupMenu(menu)
        menu.Destroy()


    def init(self):
        self.list.InsertColumn(0, _("Date:"))
        self.list.SetColumnWidth(0, 100)
        self.list.InsertColumn(1, _("Category"))
        self.list.InsertColumn(2, _("Money"))
        if self.type == 'payout':
            self.list.InsertColumn(3, _("Payment"))
            self.list.InsertColumn(4, _("Record Cycle"))
            self.list.InsertColumn(5, _("Explain"))
            self.list.SetColumnWidth(5, 300)
        else:
            self.list.InsertColumn(3, _("Record Cycle"))
            self.list.InsertColumn(4, _("Explain"))
            self.list.SetColumnWidth(4, 300)

    def load(self):
        self.list.ClearAll()
        self.init()

        year  = self.year.GetValue()
        month = self.month.GetValue()

        if self.type == 'payout':
            mytype = 0
        else:
            mytype = 1

        sql = "select * from capital where year=%s and month=%s and type=%d order by day,id" % (year, month, mytype)
        logfile.info(sql)
        rets = self.parent.parent.db.query(sql)
        if rets:
            numall = 0
            for row in rets:
                mytime = '%d-%02d-%02d' % (row['year'], row['month'], row['day'])
                item = self.list.InsertStringItem(0, mytime)
                #cate = self.parent.parent.category.payout_catemap[row['category']]
                cate = self.parent.parent.category.catemap(self.type, row['category'])
                self.list.SetStringItem(item, 1, cate)
                self.list.SetStringItem(item, 2, str(row['num']))
                self.list.SetItemData(item, row['id'])
                payway = storage.payways[row['payway']]

                cyclestr = ''
                if row['cycle'] > 0:
                    cyclestr = _('Yes')
                if self.type == 'payout':
                    self.list.SetStringItem(item, 3, payway)
                    self.list.SetStringItem(item, 4, cyclestr)
                    self.list.SetStringItem(item, 5, row['explain'])
                else:
                    self.list.SetStringItem(item, 3, cyclestr)
                    self.list.SetStringItem(item, 4, row['explain'])
                numall += row['num']
            self.total.SetValue(str(numall))
        else:
            self.total.SetValue('0')

       

    def OnChooseYear(self, event):
        self.load()

    def OnChooseMonth(self, event):
        self.load()

    
    def OnItemActivated(self, event):
        try:
            currentItem = event.m_itemIndex
        except:
            currentItem = self.currentItem
        id = self.list.GetItemData(currentItem)
        category = self.parent.parent.category
        sql = "select * from capital where id=" + str(id)
        ret = self.parent.parent.db.query(sql)
        if ret:
            row = ret[0]
            payway = storage.payways[row['payway']]
            ready = {'cates':category.catelist(self.type), 
                     'cate':category.catestr_by_id(self.type, row['category']), 'num': row['num'], 
                     'explain':row['explain'], 
                     'year':row['year'], 'month':row['month'], 'day':row['day'], 
                     'pay':payway, 'mode':'update', 'id':row['id']}

            logfile.info('ready:', ready)
            #print 'update data:', ready
            if self.type == 'payout':
                self.parent.parent.payout_dialog(ready)
            else:
                self.parent.parent.income_dialog(ready)


    def OnDelete(self, event):
        dlg = wx.MessageDialog(self, _('Is really delete? Delete can not be restored!'), _('Notice:'),
                               wx.OK | wx.CANCEL| wx.ICON_INFORMATION)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        dlg.Destroy()
 
        if self.currentItem is None:
            return
        id = self.list.GetItemData(self.currentItem)
        sql = "delete from capital where id=" + str(id)
        logfile.info('del:', sql)
        self.parent.parent.db.execute(sql)
        self.parent.parent.reload()

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        event.Skip()


class PayoutListPanel (ItemListPanel):
    type = "payout"

class IncomeListPanel (ItemListPanel):
    type = "income"


class CycleListPanel (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=0)
        self.parent = parent

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        sizer.Add(self.list, 1, wx.EXPAND|wx.ALL)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        self.currentItem = None
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnPopupMenu) 
        self.load()
   
    def OnPopupMenu(self, event):
        if not hasattr(self, "ID_POPUP_DEL"):
            self.ID_POPUP_DEL = wx.NewId()
            self.ID_POPUP_EDIT = wx.NewId()
            
            self.Bind(wx.EVT_MENU, self.OnDelete, id=self.ID_POPUP_DEL)
            self.Bind(wx.EVT_MENU, self.OnItemActivated, id=self.ID_POPUP_EDIT)
        menu = wx.Menu()
        menu.Append(self.ID_POPUP_EDIT, _("Edit"))
        menu.Append(self.ID_POPUP_DEL, _("Delete"))
        self.PopupMenu(menu)
        menu.Destroy()

    def init(self):
        self.list.InsertColumn(0, _("Type"))
        self.list.InsertColumn(1, _("Category"))
        self.list.InsertColumn(2, _("Money"))
            
        self.list.InsertColumn(3, _("Payment"))
        self.list.InsertColumn(4, _("Cycle"))

        self.list.InsertColumn(5, _("Explain"))
        self.list.SetColumnWidth(5, 300)


    def load(self):
        self.list.ClearAll()
        self.init()

        sql = "select * from recycle order by id"
        logfile.info(sql)
        rets = self.parent.parent.db.query(sql)
        if rets:
            for row in rets:
                try:
                    cate = self.parent.parent.category.catemap(row['type'], row['category'])
                    typestr = storage.catetypes[row['type']]
                except:
                    sql = "delete from recycle where id=" + str(row['id'])
                    self.parent.parent.db.execute(sql)
                    continue
                item = self.list.InsertStringItem(0, typestr)
                #self.list.SetStringItem(item, 0, storage.catetypes[row['type']]) 
                self.list.SetStringItem(item, 1, cate)
                self.list.SetStringItem(item, 2, str(row['num']))
                self.list.SetStringItem(item, 3, storage.payways[row['payway']])
                self.list.SetStringItem(item, 4, storage.cycles[row['addtime']])
                self.list.SetStringItem(item, 5, row['explain'])

                self.list.SetItemData(item, row['id'])
    
    def OnItemActivated(self, event):
        try:
            currentItem = event.m_itemIndex
        except:
            currentItem = self.currentItem
        id = self.list.GetItemData(currentItem)
        category = self.parent.parent.category

        cyclelist = []
        for k in storage.cycles:
            if type(k) != types.IntType:
                cyclelist.append(k)
        cyclelist.reverse()
    
        sql = "select * from recycle where id=" + str(id)
        ret = self.parent.parent.db.query(sql)
        if ret:
            row = ret[0]
            typestr = storage.catetypes[row['type']] 
            
            if typestr == _('Payout'):
                payout_cate = category.catestr_by_id('payout', row['category'])
                income_cate = category.income_catelist[0]
            else:
                payout_cate = category.payout_catelist[0]
                income_cate = category.catestr_by_id('income', row['category'])
 
            ready = {'payout_cates':category.payout_catelist, 'payout_cate':payout_cate, 
                 'income_cates':category.income_catelist, 'income_cate':income_cate,
                 'num':row['num'], 
                 'types':[_('Payout'), _('Income')], 'type':typestr, 
                 'cycles':cyclelist, 'cycle':storage.cycles[row['addtime']],
                 'explain':row['explain'],
                 'pay':storage.payways[row['payway']], 'mode':'update', 'id':row['id']}
            logfile.info('ready:', ready)
            #print 'update data:', ready
            self.parent.parent.cycle_dialog(ready)


    def OnDelete(self, event):
        dlg = wx.MessageDialog(self, _('Is really delete? Delete can not be restored!'), _('Notice:'),
                               wx.OK | wx.CANCEL| wx.ICON_INFORMATION)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        dlg.Destroy()
 
        if self.currentItem is None:
            return
        id = self.list.GetItemData(self.currentItem)
        sql = "delete from recycle where id=" + str(id)
        logfile.info('del:', sql)
        self.parent.parent.db.execute(sql)
        self.parent.parent.reload()

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        event.Skip()



class ContentTab (wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, -1, size=(21,21), style=wx.BK_DEFAULT)
        self.parent = parent
        self.cate = CategoryPanel(self)
        self.AddPage(self.cate, _('Category'))
        self.payoutlist = PayoutListPanel(self)
        self.AddPage(self.payoutlist, _('Payout List'))
        self.incomelist = IncomeListPanel(self)
        self.AddPage(self.incomelist, _('Income List'))
        
        self.cyclelist = CycleListPanel(self) 
        self.AddPage(self.cyclelist, _('Cycle List'))

        cates = copy.deepcopy(self.parent.category.catelist_parent())
        self.stat = statpanel.StatPanel(self, cates)
        self.AddPage(self.stat, _('Statistic'))

    def load_category(self, cate):
        self.cate.load(cate)
    

    def load_list(self):
        self.payoutlist.load()
        self.incomelist.load()

    
    def load_cycle(self):
        self.cyclelist.load()


