# coding: utf-8
import os, sys
import datetime, copy, types
import pprint
import wx
import wx.lib.sized_controls as sc
import wx.gizmos as gizmos
import wx.lib.mixins.listctrl as listmix
import logfile, statpanel, storage
import datamodel

class CategoryPanel (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=0)
        self.parent= parent        
        self.frame = self.parent.parent
        self.db = self.parent.parent.db
        self.dbx = datamodel.CategoryData(self.db)

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

        for root in [cate.payout_tree, cate.income_tree, cate.surplus_tree]:
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
            data = self.tree.GetPyData(event.GetItem())
        except:
            data = self.tree.GetPyData(self.currentItem)

        if data['id'] > 0:
            ret = self.dbx.get_ready(data['id'])
            if ret:
                self.frame.cateedit_dialog(ret)

    def OnCategoryDel(self, event):
        data = self.tree.GetPyData(self.currentItem)
        if not data or data['id'] <= 0:
            logfile.info("category data invalid.")
            return
        #frame = self.parent.parent
        ret = self.dbx.get(data['id'])
        if not ret:
            logfile.info('not found del category:', data['id'])
            return
        mytype = ret[0]['type']
        name   = ret[0]['name']
        
        if name == _('No Category'):
            dlg = wx.MessageDialog(self, _('Can not delete this category!'),
                                _('Notice:'),wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   
        else:
            dlg = wx.MessageDialog(self, _('To delete category') + '"' + name + '"' \
                                + _(', all child categories will move to "No Category"'),
                                _('Notice:'),wx.OK | wx.ICON_INFORMATION | wx.CANCEL)
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    self.dbx.delete(mytype, data['id'])
                except Exception, e:
                    wx.MessageBox(_('Delete category failure!') + str(e), 
                                _('Delete category information'), wx.OK|wx.ICON_INFORMATION)
                self.frame.reload()
            dlg.Destroy()
        
    def OnItemSelected(self, event):
        self.currentItem = event.GetItem()

class ItemListPanel (wx.Panel, listmix.ColumnSorterMixin):
    type = "payout"
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=0)
        self.parent = parent
        self.frame  = self.parent.parent
        self.db  = self.parent.parent.db
        self.dbx = datamodel.CapitalData(self.db)

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
        #self.total = wx.TextCtrl(self, -1, size=(100,-1), style=wx.TE_READONLY)
        self.total = wx.StaticText(self, -1, "", (8, 10), (60, -1))
        box.Add(self.total, 0, wx.ALIGN_CENTER)

        box.Add(wx.StaticText(self, -1, _("  Surplus: "), (8, 10)), 0, wx.ALIGN_CENTER)
        self.surplus = wx.StaticText(self, -1, "", (8, 10), (60, -1))
        box.Add(self.surplus, 0, wx.ALIGN_CENTER)

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
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnPopupMenu) 
        #self.init()
        self.itemDataMap = {}
        self.load()

        listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
   
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
        self.list.SetColumnWidth(1, 150)
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
            typeint = 0
            othertype = 1
        else:
            typeint = 1
            othertype = 0

        rets = self.dbx.get_month_by_type(self.type, year, month) 
        numall = 0
        if rets:
            for row in rets:
                item = self.list.InsertStringItem(0, row['time'])
                self.list.SetStringItem(item, 1, row['catestr'])
                self.list.SetStringItem(item, 2, str(row['num']))
                self.list.SetItemData(item, row['id'])

                if self.type == 'payout':
                    self.list.SetStringItem(item, 3, row['paywaystr'])
                    self.list.SetStringItem(item, 4, row['cyclestr'])
                    self.list.SetStringItem(item, 5, row['explain'])

                    self.itemDataMap[row['id']] = [row['time'], row['catestr'], str(row['num']), 
                                            row['paywaystr'], row['cyclestr'].encode('utf-8'), 
                                            row['explain']]
                else:
                    self.list.SetStringItem(item, 3, row['cyclestr'])
                    self.list.SetStringItem(item, 4, row['explain'])

                    self.itemDataMap[row['id']] = [row['time'], row['catestr'], str(row['num']), 
                                            row['cyclestr'].encode('utf-8'), row['explain']]
                numall += row['num']
            self.total.SetLabel(str(numall))
        else:
            self.total.SetLabel('0')

        val = self.dbx.sum_num(othertype, year, month)
        if typeint == 0: # payout
            self.surplus.SetLabel(str(val-numall))
        else:
            self.surplus.SetLabel(str(numall-val))
            
    def GetListCtrl(self):
        return self.list

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

        ret = self.dbx.get_ready(self.type, id)
        if ret:
            if self.type == 'payout':
                self.frame.payout_dialog(ret)
            else:
                self.frame.income_dialog(ret)

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
        self.dbx.delete(id)
        self.parent.parent.reload()

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        event.Skip()

    def OnColClick(self, event):
        col = event.GetColumn()
        event.Skip()


class PayoutListPanel (ItemListPanel):
    type = "payout"

class IncomeListPanel (ItemListPanel):
    type = "income"


class CycleListPanel (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=0)
        self.parent = parent
        self.frame = self.parent.parent
        self.db = self.frame.db
        self.dbx = datamodel.CycleData(self.db)

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
        self.list.SetColumnWidth(0, 50)
        self.list.InsertColumn(1, _("Category"))
        self.list.SetColumnWidth(1, 150)
        self.list.InsertColumn(2, _("Money"))
            
        self.list.InsertColumn(3, _("Payment"))
        self.list.InsertColumn(4, _("Cycle"))

        self.list.InsertColumn(5, _("Explain"))
        self.list.SetColumnWidth(5, 300)


    def load(self):
        self.list.ClearAll()
        self.init()

        rets = self.dbx.getall()
        if rets:
            for row in rets:
                item = self.list.InsertStringItem(0, row['typestr'])
                self.list.SetStringItem(item, 1, row['catestr'])
                self.list.SetStringItem(item, 2, str(row['num']))
                self.list.SetStringItem(item, 3, row['paywaystr'])
                self.list.SetStringItem(item, 4, row['addtimestr'])
                self.list.SetStringItem(item, 5, row['explain'])

                self.list.SetItemData(item, row['id'])
    
    def OnItemActivated(self, event):
        try:
            currentItem = event.m_itemIndex
        except:
            currentItem = self.currentItem
        id = self.list.GetItemData(currentItem)

        ret = self.dbx.get_ready(id)
        if ret:
            self.parent.parent.cycle_dialog(ret)

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

        self.dbx.delete(id)

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
        self.stat.reload_category(copy.deepcopy(self.parent.category.catelist_parent())) 

    def load_list(self):
        self.payoutlist.load()
        self.incomelist.load()

    
    def load_cycle(self):
        self.cyclelist.load()


