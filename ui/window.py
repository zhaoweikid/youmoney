# coding: utf-8
import os, sys, copy, time
import wx
from wx.lib.wordwrap import wordwrap
import panels, dialogs, config, storage
from loader import load_bitmap
import sqlite3, datetime, shutil
from category import Category
import pprint, traceback, logfile, version

catetypes = {0:_('Payout'), 1:_('Income'), _('Payout'):0, _('Income'):1}
payways   = {1:_('Cash'), 2:_('Credit Card'), _('Cash'):1, _('Credit Card'):2}

class MainFrame (wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(800,600),
                name=u'YouMoney', style=wx.DEFAULT_FRAME_STYLE)

        self.rundir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.bmpdir = os.path.join(self.rundir, 'images')
        icon = wx.EmptyIcon()
        iconpath = os.path.join(self.bmpdir, 'small.png')
        icon.CopyFromBitmap(wx.BitmapFromImage(wx.Image(iconpath, wx.BITMAP_TYPE_PNG)))
        self.SetIcon(icon)

        #self.conf = config.Configure()
        if config.cf:
            self.conf = config.cf
        else:
            raise ValueError, 'config.cf is None'
        
        self.lang2id = {}

        self.make_menu()
        self.make_toolbar()
        self.make_statusbar()

        self.initdb()
        self.load()
        self.book = panels.ContentTab(self)
        self.book.load_category(self.category)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.book, 1, wx.EXPAND|wx.ALL)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        wx.CallLater(100, self.notify)

    def notify(self):
        lastdb = self.conf['lastdb']
        if sys.platform.startswith('win32') and lastdb.startswith(os.environ['SystemDrive']) and self.conf.lastdb_is_default():
            wx.MessageBox(_('You db file is in default path, strongly advise save it to other path.'), _('Note:'), wx.OK|wx.ICON_INFORMATION)
        

    def initdb(self, path=None):
        if not path:
            path = self.conf['lastdb']
        self.db = storage.DBStorage(path)
        self.SetStatusText(_('Database file: ') + path, 0)
        
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
        self.book.load_list()
    
    def make_menu(self):
        self.ID_FILE_NEW  = wx.NewId()
        self.ID_FILE_OPEN = wx.NewId()
        self.ID_FILE_SAVEAS = wx.NewId()
        self.ID_FILE_EXIT = wx.NewId()
        self.ID_VIEW_LANG = wx.NewId()
        self.ID_VIEW_LANG_EN = wx.NewId()
        self.ID_VIEW_LANG_CN = wx.NewId()
        self.ID_VIEW_LANG_JP = wx.NewId()
        self.ID_ABOUT_WEBSITE = wx.NewId()
            
        self.lang2id['zh_CN'] = self.ID_VIEW_LANG_CN
        self.lang2id['en_US'] = self.ID_VIEW_LANG_EN
        self.lang2id['ja_JP'] = self.ID_VIEW_LANG_JP
        
        menubar = wx.MenuBar()
        self.filemenu = wx.Menu()
        self.filemenu.Append(self.ID_FILE_NEW, _('New database file'))
        self.filemenu.Append(self.ID_FILE_OPEN, _('Open database file'))
        self.filemenu.Append(self.ID_FILE_SAVEAS, _('Database file save as'))
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_FILE_EXIT, _('Exit'))
        menubar.Append(self.filemenu, _('File'))

       
        self.langmenu = wx.Menu()
        self.langmenu.AppendRadioItem(self.ID_VIEW_LANG_CN, _('Simple Chinese'))
        self.langmenu.AppendRadioItem(self.ID_VIEW_LANG_EN, _('English'))
        self.langmenu.AppendRadioItem(self.ID_VIEW_LANG_JP, _('Japanese'))
        
        self.viewmenu = wx.Menu()
        self.viewmenu.AppendMenu(self.ID_VIEW_LANG, _('Language'), self.langmenu)
        menubar.Append(self.viewmenu, _('View'))
        
        self.aboutmenu = wx.Menu()
        self.aboutmenu.Append(self.ID_ABOUT_WEBSITE, _('About Information'))
        menubar.Append(self.aboutmenu, _('About'))


        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnFileNew, id=self.ID_FILE_NEW)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, id=self.ID_FILE_OPEN)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAs, id=self.ID_FILE_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=self.ID_FILE_EXIT)
        self.Bind(wx.EVT_MENU, self.OnLanguage, id=self.ID_VIEW_LANG_CN)
        self.Bind(wx.EVT_MENU, self.OnLanguage, id=self.ID_VIEW_LANG_EN)
        self.Bind(wx.EVT_MENU, self.OnLanguage, id=self.ID_VIEW_LANG_JP)
        self.Bind(wx.EVT_MENU, self.OnAboutInfo, id=self.ID_ABOUT_WEBSITE)
        
        lang = self.conf['lang']
        if lang:
            mid = self.lang2id[lang]
        else:
            mid = self.ID_VIEW_LANG_EN
        self.langmenu.Check(mid, True)

    def make_toolbar(self):
        self.ID_TB_CATEEDIT = wx.NewId()
        self.ID_TB_INCOME   = wx.NewId()
        self.ID_TB_PAYOUT   = wx.NewId()
        
        self.toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.Size(48,48), wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_TEXT)
        self.toolbar.SetToolBitmapSize(wx.Size (48, 48))
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
            path = dlg.GetPath()
            logfile.info("open file:", path) 

            self.db.close()
            self.initdb(path)
            #self.db = storage.DBStorage(path)
            self.reload()
            self.conf['lastdb'] = path
            self.conf.dump()
        
        dlg.Destroy()

    def OnFileNew(self, event):
        dlg = wx.FileDialog(
            self, message="New database file save...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=_("YouMoney Database (*.db)|*.db"), style=wx.SAVE)
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            logfile.info("save file:", path) 
            if not path.endswith('.db'):
                path += ".db"
 
            if os.path.isfile(path):
                wx.MessageBox(_('File exist'), _('Can not save database file'), wx.OK|wx.ICON_INFORMATION) 
                return
 
            self.db.close()
            self.initdb(path)
            #self.db = storage.DBStorage(path)
            self.reload()
            self.conf['lastdb'] = path
            self.conf.dump()
 
        dlg.Destroy()


    def OnFileSaveAs(self, event):
        dlg = wx.FileDialog(
            self, message="Database file save as...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=_("YouMoney Database (*.db)|*.db"), style=wx.SAVE)
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            logfile.info("save file:", path) 
            if not path.endswith('.db'):
                path += ".db"
            
            self.conf.dump()
            oldfile = self.conf['lastdb']
            if os.path.isfile(path):
                wx.MessageBox(_('File exist'), _('Can not save database file'), wx.OK|wx.ICON_INFORMATION) 
                return
            try:
                shutil.copyfile(self.conf['lastdb'], path)
            except Exception, e:
                wx.MessageBox(_('Save databse file failture:') + str(e), _('Can not save database file'), wx.OK|wx.ICON_INFORMATION)
                return
            self.db.close()
            if os.path.isfile(oldfile):
                os.remove(oldfile)
            self.initdb(path)
            #self.db = storage.DBStorage(path)
            self.reload()
            self.conf['lastdb'] = path
            self.conf.dump()
        
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

        dlg = dialogs.CategoryDialog(self, ready)
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            item = dlg.values()
            logfile.info('cateedit:', item)
            type = catetypes[item['catetype']]
            parent = 0
            if item['catetype'] == _('Income'):
                if item['upcate'] != _('No Higher Category'):
                    parent = self.category.income_catemap[item['upcate']]
            elif item['catetype'] == _('Payout'):
                if item['upcate'] != _('No Higher Category'):
                    parent = self.category.payout_catemap[item['upcate']]
            
            if item['mode'] == 'insert':
                #sql = "insert into category (name,parent,type) values ('%s',%d,%d)" % (item['cate'], parent, type)
                sql = "insert into category (name,parent,type) values (?,?,?)"
                logfile.info('insert category:', sql)
                try:
                    #self.db.execute(sql, (item['cate'], parent, type, ))
                    self.db.execute_param(sql, (item['cate'], parent, type, ))
                except Exception, e:
                    wx.MessageBox(_('Add category failture:') + str(e), _('Add category information'), wx.OK|wx.ICON_INFORMATION)
                else:
                    self.reload()
            elif item['mode'] == 'update':
                #sql = "update category set name='%s',parent=%d,type=%d where id=%d" % (item['cate'], parent, type, item['id'])
                sql = "update category set name=?,parent=?,type=? where id=?"
                logfile.info('update category:', sql)
                try:
                    self.db.execute_param(sql, (item['cate'],parent,type,item['id'],))
                except Exception, e:
                    wx.MessageBox(_('Change category failture:') + str(e), _('Change category information'), wx.OK|wx.ICON_INFORMATION)
                else:
                    self.reload()
 

    def OnIncome(self, event):
        tday = datetime.date.today()
        catelist = self.category.income_catelist
        if len(catelist) == 0:
            wx.MessageBox(_('Add category first!'), _('Can not add income item'), wx.OK|wx.ICON_INFORMATION)
            return
        ready = {'cates':catelist, 'cate':catelist[0], 
                 'year':tday.year, 'month':tday.month, 'day':tday.day,
                 'num':'', 'explain':'', 'mode':'insert'}

        self.income_dialog(ready)

    def income_dialog(self, ready):
        dlg = dialogs.IncomeDialog(self, ready)
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.values()
            logfile.info('income dialog:', data)
            #sql = "insert into capital (category,num,ctime,year,month,day,payway,explain,type) values (%d,%f,%d,%d,%d,%d,%d,'%s',1)"
            sql = "insert into capital (category,num,ctime,year,month,day,payway,explain,type) values (?,?,?,?,?,?,?,?,1)"
            cate = data['cate'].split('->')[-1]

            if data['mode'] == 'insert':
                try:
                    cateid = self.category.income_catemap[cate]
                    tnow   = int(time.time())
                    num    = float(data['num'])
                    #payway = payways[data['pay']]
                    payway = 0
                    year   = data['date'].GetYear()
                    month  = data['date'].GetMonth() + 1
                    day    = data['date'].GetDay()

                    #sql = sql % (cateid, num, tnow, year, month, day, payway, data['explain'])
                    logfile.info('insert capital:', sql)
                    self.db.execute_param(sql, (cateid, num, tnow, year, month, day, payway, data['explain'],))
                except Exception, e:
                    wx.MessageBox(_('Add payout failture:') + str(e), _('Add payout information'), wx.OK|wx.ICON_INFORMATION)
                    logfile.info('insert income error:', traceback.format_exc())
                else:
                    self.reload()
            elif data['mode'] == 'update':
                #sql = "update capital set category=%d,num=%d,year=%d,month=%d,day=%d,explain='%s' where id=%d"
                sql = "update capital set category=?,num=?,year=?,month=?,day=?,explain=? where id=?"
                try:
                    cateid = self.category.income_catemap[cate]
                    num    = float(data['num'])
                    year   = data['date'].GetYear()
                    month  = data['date'].GetMonth() + 1
                    day    = data['date'].GetDay()

                    #sql = sql % (cateid, num, year, month, day, data['explain'], data['id'])
                    logfile.info('update capital:', sql)
                    self.db.execute_param(sql, (cateid, num, year, month, day, data['explain'], data['id'],))
                except Exception, e:
                    wx.MessageBox(_('Change income failture:') + str(e), _('Change income information'), wx.OK|wx.ICON_INFORMATION)
                    logfile.info('update error:', traceback.format_exc())
                else:
                    self.reload()




    def OnPayout(self, event):
        tday = datetime.date.today()
        catelist = self.category.payout_catelist
        if len(catelist) == 0:
            wx.MessageBox(_('Add category first!'), _('Can not add payout item'), wx.OK|wx.ICON_INFORMATION)
            return
 
        ready = {'cates':catelist, 'cate':catelist[0], 'num':'', 
                 'explain':'', 'year':tday.year, 'month':tday.month, 'day':tday.day,
                 'pay':_('Cash'), 'mode':'insert'}
        #print 'payout insert:', ready 
        self.payout_dialog(ready)

    def payout_dialog(self, ready):
        dlg = dialogs.PayoutDialog(self, ready)
        dlg.CenterOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.values()
            logfile.info('payout dialog:', data)
            
            cate = data['cate'].split('->')[-1]
            if data['mode'] == 'insert':
                #sql = "insert into capital (category,num,ctime,year,month,day,payway,explain,type) values (%d,%f,%d,%d,%d,%d,%d,'%s',0)"
                sql = "insert into capital (category,num,ctime,year,month,day,payway,explain,type) values (?,?,?,?,?,?,?,?,0)"
                try:
                    cateid = self.category.payout_catemap[cate]
                    tnow   = int(time.time())
                    num    = float(data['num'])
                    payway = payways[data['pay']]
                    year   = data['date'].GetYear()
                    month  = data['date'].GetMonth() + 1
                    day    = data['date'].GetDay()

                    #sql = sql % (cateid, num, tnow, year, month, day, payway, data['explain'])
                    logfile.info('insert capital payout:', sql)
                    self.db.execute_param(sql, (cateid, num, tnow, year, month, day, payway, data['explain'],))
                except Exception, e:
                    wx.MessageBox(_('Add income failture:') + str(e), _('Add income information'), wx.OK|wx.ICON_INFORMATION)
                    logfile.info('insert payout error:', traceback.format_exc())
                else:
                    self.reload()
            elif data['mode'] == 'update':
                #sql = "update capital set category=%d,num=%d,year=%d,month=%d,day=%d,payway=%d,explain='%s' where id=%d"
                sql = "update capital set category=?,num=?,year=?,month=?,day=?,payway=?,explain=? where id=?"
                try:
                    cateid = self.category.payout_catemap[cate]
                    num    = float(data['num'])
                    payway = payways[data['pay']]
                    year   = data['date'].GetYear()
                    month  = data['date'].GetMonth() + 1
                    day    = data['date'].GetDay()

                    #sql = sql % (cateid, num, year, month, day, payway, data['explain'], data['id'])
                    logfile.info('update capital:', sql)
                    self.db.execute_param(sql, (cateid, num, year, month, day, payway, data['explain'], data['id'],))
                except Exception, e:
                    wx.MessageBox(_('Change income failture:') + str(e), _('Change income information'), wx.OK|wx.ICON_INFORMATION)
                    logfile.info('update error:', traceback.format_exc())
                else:
                    self.reload()



    def OnLanguage(self, event):
        mid = event.GetId()  
        clang = self.conf['lang']
        ischange = False
        if mid == self.ID_VIEW_LANG_CN:
            if clang != 'zh_CN':
                ischange = True
            self.conf['lang'] = 'zh_CN'
            self.conf.dump()
        elif mid == self.ID_VIEW_LANG_EN:
            if not clang.startswith('en_'):
                ischange = True
            self.conf['lang'] = 'en_US'
            self.conf.dump()
        elif mid == self.ID_VIEW_LANG_JP:
            if clang != 'ja_JP':
                ischange = True
            self.conf['lang'] = 'ja_JP'
            self.conf.dump()
 

        if ischange:
            wx.MessageBox(_('Language changed! You must restart youmoney !'), _('Note:'), wx.OK|wx.ICON_INFORMATION)

    def OnAboutInfo(self, event):
        info = wx.AboutDialogInfo()
        info.Name = u"YouMoney"
        info.Version = version.VERSION
        info.Copyright = "(C) 2010 zhaoweikid"
        info.Description = wordwrap(_("YouMoney is a opensource personal finance software write by Python language.") + '\n',
            350, wx.ClientDC(self))
        info.WebSite = ("http://code.google.com/p/youmoney", _("YouMoney home page"))
        info.Developers = ["zhaoweikid"]

        info.License = wordwrap("GPL", 500, wx.ClientDC(self))
        wx.AboutBox(info)






