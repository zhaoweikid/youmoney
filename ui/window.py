# coding: utf-8
import os, sys, copy, time
import wx
import panels, dialogs, config, storage
from loader import load_bitmap
import sqlite3, datetime
from category import Category
import pprint, traceback, logfile

catetypes = {0:u'支出', 1:u'收入', u'支出':0, u'收入':1}
payways   = {1:u'现金', 2:u'信用卡', u'现金':1, u'信用卡':2}

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
        self.filemenu.Append(self.ID_FILE_OPEN, u'打开文件')
        self.filemenu.Append(self.ID_FILE_SAVE, u'保存文件')
        self.filemenu.Append(self.ID_FILE_SAVEAS, u'另存为')
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_FILE_EXIT, u'退出')
        menubar.Append(self.filemenu, u'文件')
        
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
        self.toolbar.AddLabelTool(self.ID_TB_CATEEDIT, u"添加分类", load_bitmap('images/categories.png'), shortHelp=u"添加分类", longHelp=u"添加分类") 
        self.toolbar.AddLabelTool(self.ID_TB_INCOME, u"添加收入", load_bitmap('images/cashin.png'), shortHelp=u"添加收入", longHelp=u"添加收入") 
        self.toolbar.AddLabelTool(self.ID_TB_PAYOUT, u"添加支出", load_bitmap('images/cashout.png'), shortHelp=u"添加支出", longHelp=u"添加支出") 

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
        pass

    def OnFileSave(self, event):
        pass


    def OnFileSaveAs(self, event):
        pass


    def OnCateEdit(self, event):
        ready = {'cates':[], 'cate':'', 'upcate':u'无上级分类', 'catetype':u'支出', 'mode':'insert'}
        self.cateedit_dialog(ready)


    def cateedit_dialog(self, ready):
        cates = copy.deepcopy(self.category.catelist_parent())
        cates[u'收入'].insert(0, u'无上级分类')
        cates[u'支出'].insert(0, u'无上级分类')

        ready['cates'] = cates
        if not ready['upcate']:
            ready['upcate'] = u'无上级分类'
        #ready = {'cates':cates, 'cate':'', 'upcate':u'无上级分类', 'catetype':u'支出'}

        dlg = dialogs.CategoryDialog(self, ready)
        if dlg.ShowModal() == wx.ID_OK:
            item = dlg.values()
            logfile.info(item)
            type = catetypes[item['catetype']]
            parent = 0
            if item['catetype'] == u'收入':
                if item['upcate'] != u'无上级分类':
                    parent = self.category.income_catemap[item['upcate']]
            elif item['catetype'] == u'支出':
                if item['upcate'] != u'无上级分类':
                    parent = self.category.payout_catemap[item['upcate']]
            
            if item['mode'] == 'insert':
                sql = "insert into category (name,parent,type) values ('%s',%d,%d)" % (item['cate'], parent, type)
                logfile.info(sql)
                try:
                    self.db.execute(sql)
                except Exception, e:
                    wx.MessageBox(u'添加分类失败:' + str(e), u'添加分类操作信息!', wx.OK|wx.ICON_INFORMATION)
                else:
                    self.reload()
            elif item['mode'] == 'update':
                sql = "update category set name='%s',parent=%d,type=%d where id=%d" % (item['cate'], parent, type, item['id'])
                logfile.info(sql)
                try:
                    self.db.execute(sql)
                except Exception, e:
                    wx.MessageBox(u'修改分类失败:' + str(e), u'修改分类操作信息!', wx.OK|wx.ICON_INFORMATION)
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
                loginfo.info(sql)
                self.db.execute(sql)
            except Exception, e:
                wx.MessageBox(u'添加收入信息失败: ' + str(e), u'添加收入信息', wx.OK|wx.ICON_INFORMATION)
                logfile.info(traceback.format_exc())

    def OnPayout(self, event):
        tday = datetime.date.today()
        ready = {'cates':self.category.payout_catelist, 'cate':self.category.payout_catelist[0], 'num':'', 
                 'explain':'', 'year':tday.year, 'month':tday.month, 'day':tday.day,
                 'pay':u'现金', 'mode':'insert'}
        
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
                    wx.MessageBox(u'添加支出信息失败: ' + str(e), u'添加支出信息', wx.OK|wx.ICON_INFORMATION)
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
                    wx.MessageBox(u'修改支出信息失败: ' + str(e), u'修改支出信息', wx.OK|wx.ICON_INFORMATION)
                    logfile.info(traceback.format_exc())
                else:
                    self.reload()











