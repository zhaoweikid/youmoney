# coding: utf-8
import os, sys
import datetime, time
import pprint, types
import logfile
import storage

class TreeNode:
    def __init__(self, parent, name, id):
        self.parent = parent 
        self.name = name
        self.id   = id
        self.childs = []
        self.count  = 0
        #self.num    = 0.0
        self.month_num    = 0.0
        self.day_num = 0.0

    def add_child(self, child):
        self.childs.append(child)
    
    def add_child_name(self, name, id):
        self.childs.append(TreeNode(self, name, id))

    def find(self, name):
        for ch in self.childs:
            if ch.name == name:
                return ch
        return None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def echo(self):
        print '--------------------' 
        print self.name, self.month_num, self.day_num
        for ch in self.childs:
            print '  '+ch.name, ch.month_num, ch.day_month
            for ch2 in ch.childs:
                print '    '+ch2.name, ch2.month_num, ch2.day_month
        print '--------------------' 

def treenode_find(treenode, name):
    #print 'node name:', treenode.name, 'name:', name
    if treenode.name == name:
        return treenode

    for ch in treenode.childs:
        ret = treenode_find(ch, name)
        if ret:
            return ret
    
    return None 


category = None

class Category:
    def __init__(self, caterec, rec):
        self.category_rec = caterec
        self.data_rec = rec
       
        # parent and children map , [xx->xx: 1, xx2->xx2: 2...]
        self.payout_catemap = {}
        self.income_catemap = {}
        
        # id: name
        self.idmap = {}
       
        # parent id: parent name, all category 
        self.payout_parent_catemap = {}
        self.income_parent_catemap = {}
        # cate's parent id, child id to parent id
        self.payout_parent = {}
        self.income_parent = {}
        
        # parent and children text list, [xx->xx, ...]
        self.payout_catelist = []
        self.income_catelist = []
        
        # only parent text list, [xx, ...]
        self.payout_parentlist = []
        self.income_parentlist = []
        
        # parent children relation. eg: {parent1: set([child1, child2,...]), parent2:set(), ...}
        self.payout_rela = {}
        self.income_rela = {}

        self.payout_tree = TreeNode(None, _('payout'), 0)
        self.income_tree = TreeNode(None, _('income'), 0)
        self.surplus_tree = TreeNode(None, _('surplus'), 0)
   
        self.types = {0: 'payout', 1: 'income', 'payout': 'payout', 'income': 'income'}

        self.init()

    def init(self):
        # count, month_num, day_num
        cates = [{}, {}]
        tday = datetime.date.today()
        # 统计出分类映射表
        for row in self.category_rec:
            self.idmap[row['id']] = row['name']

            if row['type'] == 0:
                #self.payout_catemap[row['name']] = row['id']
                #self.payout_catemap[row['id']]   = row['name']
                self.payout_parent[row['id']]    = row['parent']        
                #self.payout_parent[row['name']]  = row['parent']        

                #cates[0][row['name']] = [0, 0, 0]

                if row['parent'] == 0:
                    self.payout_parent_catemap[row['id']]   = row['name']
                    self.payout_parent_catemap[row['name']] = row['id']

            elif row['type'] == 1:
                #self.income_catemap[row['name']] = row['id']
                #self.income_catemap[row['id']]   = row['name']
                self.income_parent[row['id']]    = row['parent']        
                #self.income_parent[row['name']]  = row['parent']        

                #cates[1][row['name']]  = [0, 0, 0]

                if row['parent'] == 0:
                    self.income_parent_catemap[row['id']]   = row['name']
                    self.income_parent_catemap[row['name']] = row['id']


        #print 'payout_catemap:', self.payout_catemap
        #print 'income_catemap:', self.income_catemap
        #print 'payout_parent:', self.payout_parent
        #print 'income_parent:', self.income_parent
        
        parentitem = [set(), set()]
        for row in self.category_rec:
            if row['type'] == 0:
                if row['parent'] == 0: 
                    self.payout_catelist.append(row['name'])
                    self.payout_catemap[row['name']] = row['id']
                    self.payout_catemap[row['id']] = row['name']

                    self.payout_rela[row['name']] = set()
                    self.payout_tree.add_child(TreeNode(self.payout_tree, row['name'], row['id']))

                    self.payout_parentlist.append(row['name'])

                    cates[0][row['name']] = [0, 0, 0]
                else:
                    parentstr = self.payout_parent_catemap[row['parent']]
                    s = '%s->%s' % (parentstr, row['name'])
                    self.payout_catelist.append(s)
                    self.payout_catemap[s] = row['id']
                    self.payout_catemap[row['id']] = s

                    parentitem[0].add(parentstr)
                        
                    cates[0][s] = [0, 0, 0]

                    self.payout_rela[parentstr].add(row['name'])
                    node = self.payout_tree.find(parentstr)
                    if node:
                        node.add_child_name(row['name'], row['id'])

            elif row['type'] == 1:
                if row['parent'] == 0: 
                    self.income_catelist.append(row['name'])
                    self.income_catemap[row['name']] = row['id']
                    self.income_catemap[row['id']] = row['name']
  
                    self.income_rela[row['name']] = set()
                    self.income_tree.add_child_name(row['name'], row['id'])
                    self.income_parentlist.append(row['name'])
                    cates[1][row['name']]  = [0, 0, 0]
                else:
                    parentstr = self.income_parent_catemap[row['parent']]
                    s = '%s->%s' % (parentstr, row['name'])
                    self.income_catelist.append(s)
                    self.income_catemap[s] = row['id']
                    self.income_catemap[row['id']] = s

                    parentitem[1].add(parentstr)

                    cates[1][s]  = [0, 0, 0]

                    self.income_rela[parentstr].add(row['name'])
                    node = self.income_tree.find(parentstr)
                    if node:
                        node.add_child_name(row['name'], row['id'])

        #print 'payout_rela:', self.payout_rela
        #print 'income_rela:', self.income_rela
        
        for k in parentitem[0]:
            self.payout_catelist.remove(k)

        for k in parentitem[1]:
            self.income_catelist.remove(k)
        
        # compute num
        #print 'data:', self.data_rec
        #pprint.pprint(self.payout_rela)
        for row in self.data_rec:
            cateid = row['category']
            if row['type'] == 0:
                catestr = self.payout_catemap[cateid]
            else:
                catestr = self.income_catemap[cateid]
            #print 'catestr:', catestr
            x = cates[row['type']][catestr] 
            x[0] += 1
            x[1] += row['num']
            if row['day'] == tday.day:
                x[2] += row['num']

        #pprint.pprint(cates)
        #for kk in cates:
        #    keys = kk.keys()
        #    keys.sort()
        #    for kk1 in keys:
        #        print kk1, kk[kk1]
        #    print
        #print '-' * 30

        for k in cates[0]: 
            pos = k.find('->')
            #p = self.payout_parent[k]
            #print 'parent:', k, p
            if pos > 0:
                p = k[:pos]
                v1 = cates[0][k]
                vv = cates[0][p]
                vv[0] += v1[0]
                vv[1] += v1[1]
                vv[2] += v1[2]

        #pprint.pprint(cates)
        #for kk in cates:
        #    keys = kk.keys()
        #    keys.sort()
        #    for kk1 in keys:
        #        print kk1, kk[kk1]
        #    print
        #print '-' * 30


        for k in cates[1]: 
            pos = k.find('->')
            #p = self.income_parent[k]
            if pos > 0:
                p = k[:pos]
                v1 = cates[1][k]
                vv = cates[1][p]
                vv[0] += v1[0]
                vv[1] += v1[1]
                vv[2] += v1[2]
        
        #pprint.pprint(cates)
       
        mtotal = 0
        dtotal = 0
        for k in cates[0]:
            v = cates[0][k]
            kn = k.split('->')[-1]
            node = treenode_find(self.payout_tree, kn)
            if node:
                node.count = v[0]
                node.month_num = v[1]
                node.day_num   = v[2]
                if not node.childs:
                    mtotal += v[1]
                    dtotal += v[2]
            #self.payout_tree.echo()
        self.payout_tree.month_num = mtotal
        self.payout_tree.day_num = dtotal

        #self.payout_tree.echo()
        
        mtotal = 0
        dtotal = 0
        for k in cates[1]:
            node = None
            v = cates[1][k]
            kn = k.split('->')[-1]
            node = treenode_find(self.income_tree, kn)
            if node:
                node.count = v[0]
                node.month_num = v[1]
                node.day_num   = v[2]
                if not node.childs:
                    mtotal += v[1]
                    dtotal += v[2]
        self.income_tree.month_num = mtotal
        self.income_tree.day_num = dtotal
        #self.income_tree.echo()

        self.surplus_tree.month_num = self.income_tree.month_num - self.payout_tree.month_num


    def catelist(self, ctype=None):
        '''所有类别的列表, 每项为 parent->child'''
        if ctype is None:
            return {_('Payout'):self.payout_catelist, _('Income'):self.income_catelist}
        elif ctype == 'payout' or ctype == 0:
            return self.payout_catelist
        elif ctype == 'income' or ctype == 1:
            return self.income_catelist
        return None
   
    def catelist_parent(self):
        '''所有一级类别列表'''
        return {_('Payout'):self.payout_parentlist, _('Income'):self.income_parentlist}

    
    def parent_cate_id(self, catype, name):
        '''查询某项类别的父类id'''
        castr = self.types[catype]
        parent_dict  = getattr(self, castr + '_parent')

        if type(name) != types.IntType:
            catemap_dict  = getattr(self, castr + '_catemap')
            return parent_dict[catemap_dict[name]]
        return parent_dict[name]


    def parent_cate_name(self, catype, name):
        '''查询某项类别的父类名'''
        castr = self.types[catype]
        parent_dict  = getattr(self, castr + '_parent')
        catemap_dict = getattr(self, castr + '_catemap')
 
        if type(name) != types.IntType:
            cid = parent_dict[catemap_dict[name]]
        else:
            cid = name
         
        p = parent_dict[cid]
        if p == 0:
            return ''
        else:
            return catemap_dict[p]

    def catestr_by_id(self, catype, cid):
        '''根据id查询名字，名字形式为 parent->child'''
        castr = self.types[catype]
        catemap_dict = getattr(self, castr + '_catemap')
        return catemap_dict[cid]

    def catemap(self, catype, name):
        '''根据id或parent->child互查'''
        castr = self.types[catype]
        catemap_dict = getattr(self, castr + '_catemap')
        return catemap_dict[name]

    def catemap_by_id(self, catype, cid):
        return catestr_by_id(catype, cid)

    def cate_subs_id(self, catype, name):
        castr = self.types[catype]
        catemap_dict = getattr(self, castr + '_catemap')
        if type(name) == types.IntType:
            namestr = self.idmap[name]
        else:
            namestr = name
        rela_dict  = getattr(self, castr + '_rela')
        ret = rela_dict[namestr]

        if ret:
            return [ catemap_dict[namestr + '->' + k] for k in ret ]
        return [catemap_dict[namestr]]


class CategoryData:
    def __init__(self, conn):
        self.db = conn

    def count(self):
        sql = "select count(*) from category"
        return self.db.query_one(sql) 

    def getall(self, order=None):
        if not order:
            sql = "select * from category"
        else:
            sql = "select * from category order by " + order
        return self.db.query(sql)

    def getid(self, type, name, parent=None):
        sql = "select id from category where name='%s' and type=%d" % (name, type)
        if parent:
            sql += " and parent=%d" % (parent)
        return self.db.query_one(sql)

    def get(self, cid=None):
        if cid:
            sql = "select * from category where id=" + str(cid) 
        else:
            sql = "select * from category order by parent"
        ret = self.db.query(sql)
        return ret

    def get_ready(self, cid):
        ret = self.get(cid)
        if ret:
            row = ret[0]
            if row['parent'] > 0:
                upcate = category.catemap(row['type'], row['parent'])
            else:
                upcate = _("No Higher Category")
            if row['type'] == 0:
                ct = _('Payout')
            else:
                ct = _('Income')
            ready = {'cates':[], 'cate':row['name'], 'upcate':upcate, 
                     'catetype':ct, 'mode':'update', 'id':row['id']}
            return ready
        return None
    
    def delete(self, mytype, cid):
        '''mytype: category type, cid: category id'''
        # 检查要删除的所有分类，包括子类
        logfile.info('delete category:', mytype, cid)
        idlist = [str(cid)]
        sql = "select * from category where parent=" + str(cid)
        ret = self.db.query(sql)
        if ret:
            for row in ret:
                idlist.append(str(row['id']))
        ids = ','.join(idlist)
        # 检查是否有"未分类", 没有需要创建
        sql = u"select * from category where name='%s' and type=%d" %(_('No Category'), mytype)
        ret = self.db.query(sql)
        if not ret:
            sql = "insert into category (name,parent,type) values ('%s',0,%d)" % (_('No Category'), mytype) 
            self.db.execute(sql)
            sql = u"select * from category where name='%s' and type=%d" % (_('No Category'), mytype)
            ret = self.db.query(sql)    
        # "未分类"的id
        mycid = ret[0]['id']

        # 更新
        try:
            # 使用该分类的记录，都要改为"未分类"
            sql = "update capital set category=%d where category in (%s) and type=%d" % (mycid, ids, mytype)
            logfile.info('update category:', sql)
            self.db.execute(sql, False)
            # 循环纪录使用该分类的，要改为"未分类"
            sql = "update recycle set category=%d where category in (%s) and type=%d" % (mycid, ids, mytype)
            logfile.info('update recycle:', sql)
            self.db.execute(sql, False)
            # 删除该分类
            sql = "delete from category where id=%d or parent=%d" % (cid, cid)
            self.db.execute(sql, False)
        except:
            self.db.rollback()
        else:
            self.db.commit()

    def insert(self, typeint, parent, cate):
        sql = "insert into category (name,parent,type) values (?,?,?)"
        logfile.info('insert category:', sql)
        self.db.execute_param(sql, (cate, parent, typeint, ))
   
    def _convert_item(self, item):
        type = storage.catetypes[item['catetype']]
        parent = 0            
        if item['catetype'] == _('Income'):
            if item['upcate'] != _('No Higher Category'):
                parent = self.category.income_catemap[item['upcate']]
        elif item['catetype'] == _('Payout'):
            if item['upcate'] != _('No Higher Category'):
                parent = self.category.payout_catemap[item['upcate']]
        return type, parent
 
    def insert_item(self, item):
        typeint, parent = self._convert_item(item)
        return self.insert(typeint, parent, item['cate'])

    def update(self, cid, typeint, parent, cate):
        sql = "update category set name=?,parent=?,type=? where id=?"
        logfile.info('update category:', sql)
        self.db.execute_param(sql, (cate,parent,typeint,cid,))
 
    def update_item(self, item):
        typeint, parent = self._convert_item(item)
        return self.update(item['id'], typeint, parent, item['cate'])

class CapitalData:
    def __init__(self, conn):
        self.db = conn

    def getall(self, order=None):
        if not order:
            sql = "select * from capital"
        else:
            sql = "select * from capital order by " + order
        return self.db.query(sql)

    def get_month_by_type(self, typestr, year, month):
        if typestr == 'payout':
            typeint = 0
        else:
            typeint = 1
        sql = "select * from capital where year=%s and month=%s and type=%d order by day,id" % \
                (year, month, typeint)
        logfile.info(sql)
        rets = self.db.query(sql)
        if rets:
            for row in rets:                
                mytime = '%d-%02d-%02d' % (row['year'], row['month'], row['day'])
                row['time']      = mytime
                row['catestr']   = category.catemap(typestr, row['category'])
                row['paywaystr'] = storage.payways[row['payway']]
                cyclestr = ''                
                if row['cycle'] > 0:
                    cyclestr = _('Yes')
                row['cyclestr'] = cyclestr 
        return rets

    def get_month(self, year, month):
        sql = "select * from capital where year=%d and month=%d" % (year, month)
        return self.db.query(sql)

    def sum_num(self, typeint, year, month):
        sql = "select sum(num) as num from capital where year=%s and month=%s and type=%s" % \
                (year, month, typeint)
        rets = self.db.query(sql)
        if rets:
            if not rets[0]['num']:
                return 0
            else:
                return rets[0]['num']
        return 0

    def get(self, cid):
        sql = "select * from capital where id=" + str(cid)
        return self.db.query(sql)
 
    def get_ready(self, typestr, cid):
        sql = "select * from capital where id=" + str(cid)
        ret = self.db.query(sql)
        if ret:
            row = ret[0]
            payway = storage.payways[row['payway']]
            ready = {'cates':category.catelist(typestr),
                     'cate':category.catestr_by_id(typestr, row['category']), 'num': row['num'],
                     'explain':row['explain'],
                     'year':row['year'], 'month':row['month'], 'day':row['day'],
                     'pay':payway, 'mode':'update', 'id':row['id']}

            logfile.info('ready:', ready)
            return ready
        return None

    def delete(self, cid):
        sql = "delete from capital where id=" + str(cid)
        logfile.info('del:', sql)
        self.db.execute(sql)

    def insert(self, category, num, ctime, year, month, day, payway, explain, type):
        sql = "insert into capital(category,num,ctime,year,month,day,payway,explain,type) values (?,?,?,?,?,?,?,?,?)"            
        param = (category, num, ctime, year, month, day, payway, explain.encode('utf-8'), type)
        self.db.execute_param(sql, param)
 
 
    def insert_income(self, data):
        sql = "insert into capital (category,num,ctime,year,month,day,payway,explain,type) values (?,?,?,?,?,?,?,?,1)"
        #cate = data['cate'].split('->')[-1]

        cateid = category.income_catemap[data['cate']]
        tnow   = int(time.time())
        num    = float(data['num'])
        payway = 0
        year   = data['date'].GetYear()
        month  = data['date'].GetMonth() + 1
        day    = data['date'].GetDay()

        logfile.info('insert capital:', sql)
        self.db.execute_param(sql, (cateid, num, tnow, year, month, day, payway, data['explain'],))

    def insert_payout(self, data):
        #cate = data['cate'].split('->')[-1]
        sql = "insert into capital (category,num,ctime,year,month,day,payway,explain,type) values (?,?,?,?,?,?,?,?,0)"
        #cateid = self.category.payout_catemap[cate]
        cateid = category.payout_catemap[data['cate']]
        tnow   = int(time.time())
        num    = float(data['num'])
        payway = storage.payways[data['pay']]
        year   = data['date'].GetYear()
        month  = data['date'].GetMonth() + 1
        day    = data['date'].GetDay()

        #sql = sql % (cateid, num, tnow, year, month, day, payway, data['explain'])
        logfile.info('insert capital payout:', sql)
        self.db.execute_param(sql, (cateid, num, tnow, year, month, day, payway, data['explain'],))
    
    def update_income(self, data):
        sql = "update capital set category=?,num=?,year=?,month=?,day=?,explain=? where id=?"
        cateid = category.income_catemap[data['cate']]
        num    = float(data['num'])
        year   = data['date'].GetYear()
        month  = data['date'].GetMonth() + 1
        day    = data['date'].GetDay()

        #sql = sql % (cateid, num, year, month, day, data['explain'], data['id'])
        logfile.info('update capital:', sql)
        self.db.execute_param(sql, (cateid, num, year, month, day, data['explain'], data['id'],))

    def update_payout(self, data):
        sql = "update capital set category=?,num=?,year=?,month=?,day=?,payway=?,explain=? where id=?"
        #cateid = self.category.payout_catemap[cate]
        cateid = category.payout_catemap[data['cate']]
        num    = float(data['num'])
        payway = storage.payways[data['pay']]
        year   = data['date'].GetYear()
        month  = data['date'].GetMonth() + 1
        day    = data['date'].GetDay()

        #sql = sql % (cateid, num, year, month, day, payway, data['explain'], data['id'])
        logfile.info('update capital:', sql)
        self.db.execute_param(sql, (cateid, num, year, month, day, 
                              payway, data['explain'], data['id'],))


    def stat(self, qtype, mytype, catestr, 
            fromdate, fromyear, frommonth, fromday, todate, 
            toyear, tomonth, today, minmonth, maxmonth):
        endsql = ''
        if catestr != _('All Categories'):
            logfile.info("cate:", catestr)
            cates = category.cate_subs_id(mytype, catestr)
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
        rets = self.db.query(sql)
        if not rets:
            rets = []
        logfile.info('rets:', rets)
        return rets, (fromyear, frommonth), (toyear, tomonth)


class CycleData:
    def __init__(self, conn):
        self.db = conn

    def getall(self):
        sql = "select * from recycle order by id"
        logfile.info(sql)
        rets = self.db.query(sql)
        if rets:
            #for row in rets:
            delx = []
            for i in range(0, len(rets)):
                row = rets[i]
                try:
                    catestr = category.catemap(row['type'], row['category'])
                    typestr = storage.catetypes[row['type']]
                    row['catestr'] = catestr
                    row['typestr'] = typestr
                    row['paywaystr']  = storage.payways[row['payway']]
                    row['addtimestr'] = storage.cycles[row['addtime']]
                except:
                    sql = "delete from recycle where id=" + str(row['id'])
                    self.db.execute(sql)
                    delx.append(i)
                    continue
            if delx:
                delx.reverse() 
                for i in delx:
                    del self.rets[i]
            

        return rets
 
    def get(self, cid):
        sql = "select * from recycle where id=" + str(cid)
        return self.db.query(sql)
 
    def get_ready(self, cid):
        cyclelist = []
        for k in storage.cycles:
            if type(k) != types.IntType:
                cyclelist.append(k)
        cyclelist.reverse()

        sql = "select * from recycle where id=" + str(cid)
        ret = self.db.query(sql)
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
            return ready
        return None

    def delete(self, cid):
        sql = "delete from recycle where id=" + str(cid)
        logfile.info('del:', sql)
        self.db.execute(sql)

    def insert(self, data):
        #cate = data['cate'].split('->')[-1]
        sql = "insert into recycle (category,num,ctime,payway,type,addtime,explain) values (?,?,?,?,?,?,?)"
        typeid = storage.catetypes[data['type']]
        if data['type'] == _('Payout'):
            cateid = category.payout_catemap[data['cate']]
        else:
            cateid = category.income_catemap[data['cate']]
        tnow   = int(time.time())
        num    = float(data['num'])
        payway = storage.payways[data['pay']]
        addtime= storage.cycles[data['addtime']]

        logfile.info('insert cycle:', sql)
        self.db.execute_param(sql, (cateid, num, tnow, payway, typeid, addtime, data['explain'],))

    def update(self, data):
        #cate = data['cate'].split('->')[-1]
        sql = "update recycle set category=?,num=?,payway=?,type=?,addtime=?,explain=? where id=?"
        typeid = storage.catetypes[data['type']]
        if data['type'] == _('Payout'):
            cateid = category.payout_catemap[data['cate']]
        else:
            cateid = category.income_catemap[data['cate']]

        num    = float(data['num'])
        payway = storage.payways[data['pay']]
        addtime= storage.cycles[data['addtime']]

        logfile.info('update cycle:', sql)
        self.db.execute_param(sql, (cateid, num, payway, typeid, addtime, data['explain'], data['id'],))

class UserData:
    def __init__(self, db):
        self.db = db
    
    def password(self):
        sql = "select * from user" 
        ret = self.db.query(sql)
        if ret:
            return ret[0]['password']
        return None
            
    def change_password(self, newpass):
        sql = "update user set password=?,mtime=?"
        self.db.execute_param(sql, (newpass, int(time.time()),))

class VerinfoData:
    def __init__(self, db):
        self.db = db

    def first_time(self):
        sql = "select sync_first_time from verinfo"
        return self.db.query_one(sql)

    def up_first_time(self):
        sql = "update verinfo set sync_first_time=%d" % int(time.time())
        return self.db.execute(sql)


