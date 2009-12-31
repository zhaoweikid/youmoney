# coding: utf-8
import os, sys, copy, time
import wx
import panels, dialogs, config, storage
from loader import load_bitmap
import sqlite3, datetime
from category import Category
import pprint, traceback, logfile

catetypes = {0:_('Payout'), 1:_('Income'), _('Payout'):0, _('Income'):1}
payways   = {1:_('Cash'), 2:_('Credit Card'), _('Cash'):1, _('Credit Card'):2}

class MainFrame (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(800,600),
                name=u'YouMoney', style=wx.DEFAULT_FRAME_STYLE)

        self.rundir = os.path.dirname(os.path.abspath(sys.argv[0]))
        try:
            self.conf   = config.Configure()
        except:
            pass
        
        self.make_menu()
        self.make_toolbar()
        self.make_statusbar()

        self.init()
        self.load()
        self.book = panels.ContentTab(self)
        self.book.load_category(self.category)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.book, 1, wx.EXPAND|wx.ALL)
        self.SetSizer(sizer)
        #self.SetAutoLayout(True)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        

    def init(self):
        self.db = storage.DBStorage(os.path.join(self.rundir, "data", "youmoney.db"))
        
    def load(self):
        tday = datetime.date.today()
        sql = "select * from category order by parent"
        cates = self.db.query(sql)
        sql = "select * from capital where year=%d and month=%d" % (tday.year, tday.month)
        recs  = self.db.query(sql)
   
        self.category = Category(cates, recs)

    
    def reload(self):
        self.load()
        self.book.load_category(self.category)
        self.book.load_payout()
    
    def make_menu(self):
        self.ID_FILE_OPEN = wx.NewId()
        self.ID_FILE_SAVE = wx.NewId()
        self.ID_FILE_SAVEAS = wx.NewId()
        self.ID_FILE_EXIT = wx.NewId()
        
        menubar = wx.MenuBar()
        self.filemenu = wx.Menu()
        self.filemenu.Append(self.ID_FILE_OPEN, _('Open database file'))
        self.filemenu.Append(self.ID_FILE_SAVE, _('Save database file'))
        self.filemenu.Append(self.ID_FILE_SAVEAS, _('Save as'))
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_FILE_EXIT, _('Exit'))
        menubar.Append(self.filemenu, _('File'))
        
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnFileOpen, id=self.ID_FILE_OPEN)
        self.Bind(wx.EVT_MENU, self.OnFileSave, id=self.ID_FILE_SAVE)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAs, id=self.ID_FILE_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=self.ID_FILE_EXIT)

    def make_toolbar(self):
        self.ID_TB_CATEEDIT = wx.NewId()
        self.ID_TB_INCOME   = wx.NewId()
        self.ID_TB_PAYOUT   = wx.NewId()
        
        self.toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.Size(64,64), wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_TEXT)
        self.toolbar.SetToolBitmapSize(wx.Size (64, 64))
        self.toolbar.AddLabelTool(self.ID_TB_CATEEDIT, _('Add Category'), load_bitmap('images/categories.png'), shortHelp=_('Add Category'), longHelp=_('Add Category')) 
        self.toolbar.AddLabelTool(self.ID_TB_INCOME, _('Add Income'), load_bitmap('images/cashin.png'), shortHelp=_('Add Income'), longHelp=_('Add Income')) 
        self.toolbar.AddLabelTool(self.ID_TB_PAYOUT, _("Add Payout"), load_bitmap('images/cashout.png'), shortHelp=_("Add Payout"), longHelp=_("Add Payout")) 

        self.toolbar.Realize ()
        self.SetToolBar(self.toolbar)

        self.Bind(wx.EVT_TOOL, self.OnCateEdit, id=self.ID_TB_CATEEDIT)
        self.Bind(wx.EVT_TOOL, self.OnIncome, id=self.ID_TB_INCOME)
        self.Bind(wx.EVT_TOOL, self.OnPayout, id=self.ID_TB_PAYOUT)



    def make_statusbar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(1)
        self.SetStatusWidths([-1])


    def OnCloseWindow(self, event):
        self.Destroy()
        sys.exit() 


    def OnFileOpen(self, event):
        dlg = wx.FileDialog(
            self, message=_("Choose database file:"),
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=_("YouMoney Database (*.db)|*.db"),
            style=wx.OPEN | wx.CHANGE_DIR
            )

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPath()
            logfile.info("open file:", paths) 
        
        dlg.Destroy()

    def OnFileSave(self, event):
        dlg = wx.FileDialog(
            self, message=_("Database file save..."), defaultDir=os.getcwd(), 
            defaultFile="", wildcard=_("YouMoney Database (*.db)|*.db"), style=wx.SAVE)
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            logfile.info("save file:", paths) 
        
        dlg.Destroy()

    def OnFileSaveAs(self, event):
        dlg = wx.FileDialog(
            self, message="Database file save...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=_("YouMoney Database (*.db)|*.db"), style=wx.SAVE)
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            logfile.info("save file:", paths) 
        
        dlg.Destroy()



    def OnCateEdit(self, event):
        ready = {'cates':[], 'cate':'', 'upcate':_('No Higher Category'), 'catetype':_('Payout'), 'mode':'insert'}
        self.cateedit_dialog(ready)


    def cateedit_dialog(self, ready):
        cates = copy.deepcopy(self.category.catelist_parent())
        cates[_('Income')].insert(0, _('No Higher Category'))
        cates[_('Payout')].insert(0, _('No Higher Category'))

        ready['cates'] = cates
        if not ready['upcate']:
            ready['upcate'] = _('No Higher Category')
        #ready = {'cates':cates, 'cate':'', 'upcate':u'无上级分类', 'catetype':u'支出'}

        dlg = dialogs.CategoryDialog(self, ready)
        if dlg.ShowModal() == wx.ID_OK:
            item = dlg.values()
            logfile.info(item)
            type = catetypes[item['catetype']]
            parent = 0
            if item['catetype'] == _('Income'):
                if item['upcate'] != _('No Higher Category'):
                    parent = self.category.income_catemap[item['upcate']]
            elif item['catetype'] == _('Payout'):
                if item['upcate'] != _('No Higher Category'):
                    parent = self.category.payout_catemap[item['upcate']]
            
            if item['mode'] == 'insert':
                sql = "insert into category (name,parent,type) values ('%s',%d,%d)" % (item['cate'], parent, type)
                logfile.info(sql)
                try:
                    self.db.execute(sql)
                except Exception, e:
                    wx.MessageBox(_('Add category failture:') + str(e), _('Add category information'), wx.OK|wx.ICON_INFORMATION)
                else:
                    self.reload()
            elif item['mode'] == 'update':
                sql = "update category set name='%s',parent=%d,type=%d where id=%d" % (item['cate'], parent, type, item['id'])
                logfile.info(sql)
                try:
                    self.db.execute(sql)
                except Exception, e:
                    wx.MessageBox(_('Change category failture:') + str(e), _('Change category information'), wx.OK|wx.ICON_INFORMATION)
                else:
                    self.reload()
 

    def OnIncome(self, event):
        tday = datetime.date.today()
        ready = {'cates':self.category.income_catelist, 'cate':self.category.income_catelist[0], 
                 'year':tday.year, 'month':tday.month, 'day':tday.day,
                 'num':'', 'explain':'', 'mode':'insert'}

        self.income_dialog(ready)

    def income_dialog(self, ready):
        dlg = dialogs.IncomeDialog(self, ready)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.values()
            logfile.info(data)
            sql = "insert into capital (category,num,ctime,year,month,day,payway,explain,type) values (%d,%f,%d,%d,%d,%d,%d,'%s',1)"
            cate = data['cate'].split('->')[-1]
            try:
                cateid = self.category.income_catemap[cate]
                tnow   = int(time.time())
                num    = float(data['num'])
                #payway = payways[data['pay']]
                payway = 0
                year   = data['date'].GetYear()
                month  = data['date'].GetMonth() + 1
                day    = data['date'].GetDay()

                sql = sql % (cateid, num, tnow, year, month, day, payway, data['explain'])
                logfile.info(sql)
                self.db.execute(sql)
            except Exception, e:
                wx.MessageBox(_('Add payout failture:') + str(e), _('Add payout information'), wx.OK|wx.ICON_INFORMATION)
                logfile.info(traceback.format_exc())
            else:
                self.reload()

    def OnPayout(self, event):
        tday = datetime.date.today()
        ready = {'cates':self.category.payout_catelist, 'cate':self.category.payout_catelist[0], 'num':'', 
                 'explain':'', 'year':tday.year, 'month':tday.month, 'day':tday.day,
                 'pay':_('Cash'), 'mode':'insert'}
        #print 'payout insert:', ready 
        self.payout_dialog(ready)

    def payout_dialog(self, ready):
        dlg = dialogs.PayoutDialog(self, ready)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.values()
            logfile.info(data)
            
            cate = data['cate'].split('->')[-1]
            if data['mode'] == 'insert':
                sql = "insert into capital (category,num,ctime,year,month,day,payway,explain,type) values (%d,%f,%d,%d,%d,%d,%d,'%s',0)"
                try:
                    cateid = self.category.payout_catemap[cate]
                    tnow   = int(time.time())
                    num    = float(data['num'])
                    payway = payways[data['pay']]
                    year   = data['date'].GetYear()
                    month  = data['date'].GetMonth() + 1
                    day    = data['date'].GetDay()

                    sql = sql % (cateid, num, tnow, year, month, day, payway, data['explain'])
                    logfile.info(sql)
                    self.db.execute(sql)
                except Exception, e:
                    wx.MessageBox(_('Add income failture:') + str(e), _('Add income information'), wx.OK|wx.ICON_INFORMATION)
                    logfile.info(traceback.format_exc())
                else:
                    self.reload()
            elif data['mode'] == 'update':
                sql = "update capital set category=%d,num=%d,year=%d,month=%d,day=%d,payway=%d,explain='%s' where id=%d"
                try:
                    cateid = self.category.payout_catemap[cate]
                    num    = float(data['num'])
                    payway = payways[data['pay']]
                    year   = data['date'].GetYear()
                    month  = data['date'].GetMonth() + 1
                    day    = data['date'].GetDay()

                    sql = sql % (cateid, num, year, month, day, payway, data['explain'], data['id'])
                    logfile.info(sql)
                    self.db.execute(sql)
                except Exception, e:
                    wx.MessageBox(_('Change income failture:') + str(e), _('Change income information'), wx.OK|wx.ICON_INFORMATION)
                    logfile.info(traceback.format_exc())
                else:
                    self.reload()











