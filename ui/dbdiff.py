# coding: utf-8
import os, sys
import types
import sqlite3
import logfile

class DBDiff:
    def __init__(self, cate, newdbfile, olddbfile):
        self.cate = cate

        self.newdbfile = newdbfile
        self.olddbfile = olddbfile
        
        self.olddb = sqlite3.connect(olddbfile)
        self.newdb = sqlite3.connect(newdbfile)

        self.tablesid = {'category':'id,name,parent,type'], 
                    'capital':'id,category,num,year,month,day,payway,explain,type,cycle', 
                    'recycle':'id,category,payway,type,addtime,explain,lasttime'}

        self.tableone = {'user':'password,mtime', 
                         #'verinfo':'version,sys,sync_first_time'
                        }
       
        
        self.tabledesc = {'category':[_('Category'), ['ID',_('Category'),_('Higher Category'),_('Type')]],
                          'captial':[_('Capital'), ['ID', _('Category'), _('Money'), 
                                                    _('Date:'), _('Payway'),
                                                    _('Explain'), _('Type'), _('Cycle')]], 
                          'recycle':[_('Recycle'), ['ID', _('Category'), _('Payway'), _('Type'),
                                                    _('Add Time'), _('Explain'), _('Last Time')]],
                          'user':[_('User'), [_('Password'), _('Modify Time')]],
                         }
        #self.tabledesc = {'category':u"ID,分类,上级分类,类型",
        #                  'capital':u"ID,分类,金额,创建时间,年,月,日,支付方式,说明,类型,循环记录",
        #                  'recycle':u"ID,分类,创建时间,支付方式,类型,添加时间,说明,最后循环时间",
        #                  'user':u"密码,修改时间",
        #                  'verinfo':u"版本,系统,第一次同步时间"}

        self.fsep = "$#$"


    def close(self):
        if self.olddb:
            self.olddb.close()
        self.olddb = None
        if self.newdb:
            self.newdb.close()
            self.newdb = None

    def query(self, db, sql, isdict=False):
        if type(sql) == types.UnicodeType:
            sql = sql.encode(self.charset, 'ignore')
 
        cur = db.cursor()
        cur.execute(sql)
 
        res = cur.fetchall()
        ret = []

        if res and isdict:
            des = cur.description
            names = [x[0] for x in des]
            for line in res:
                ret.append(dict(zip(names, line))) 
        else:
            ret = res 

        cur.close()
        return ret 

    def diff(self):
        result = {}
        for tbl,fields in self.tablesid.iteritems():
            newset, oldset = self.table_diff_by_id(tbl, fields)
            logfile.info('diff1:', newset, oldset)

            if newset or oldset:
                result[tbl] = [fields.split(','), self.difftran(newset), self.difftran(oldset)]

        for tbl,fields in self.tableone.iteritems():
            newstr, oldstr = self.table_diff_one(tbl, fields)
            logfile.info('diff2:', newstr, oldstr)
        
            if newstr or oldstr:
                result[tbl] = [fields.split(','), self.difftran(newstr), self.difftran(oldstr)]

        return result

    def difftran(self, items, fields=None):
        #fieldlist = fields.split(',')
        if not items:
            return []

        ret = []

        if type(items) == types.StringType or type(items) == types.UnicodeType:
            ret.append(items.split(self.fsep))
        else:
            for item in items:
                itemlist  = item.split(self.fsep) 
                ret.append(itemlist)

        return ret


    def table_diff_by_id(self, table, fields):
        logfile.info('table:', table)
        fieldslist = fields.split(',')
        newdb_lastid = 0
        olddb_lastid = 0
        length  = 1000

        sql = "select %s from %s order by id limit %d,%d"

        newset = set()
        oldset = set()

        while True:
            newsql = sql % (fields, table, newdb_lastid, length)
            oldsql = sql % (fields, table, olddb_lastid, length)

            newret = self.query(self.newdb, newsql)
            if newret:
                for row in newret:
                    xs = []
                    for i in range(0, len(row)):
                        f = row[i]
                        if type(f) == types.UnicodeType:
                            f = f.encode('utf-8')
                        xs.append(str(f))
                    newset.add(self.fsep.join(xs))

                newdb_lastid = newret[-1][0]

            oldret = self.query(self.olddb, oldsql)
            if oldret:
                for row in oldret:
                    xs = []
                    for i in range(0, len(row)):
                        f = row[i]
                        if type(f) == types.UnicodeType:
                            f = f.encode('utf-8')
                        xs.append(str(f))

                    oldset.add(self.fsep.join(xs))
                olddb_lastid = oldret[-1][0]

            if not newret and not oldret:
                break
        
            #logfile.info('new:', len(newset), 'old:', len(oldset))
            newdiff = newset.difference(oldset)
            #logfile.info('newdiff:', newdiff) 
            olddiff = oldset.difference(newset)
            #logfile.info('olddiff:', olddiff) 

            newset = newdiff
            oldset = olddiff

        #logfile.info('new:', newset, 'old:', oldset)
        return newdiff, olddiff

    def table_diff_one(self, table, fields):
        logfile.info('table:', table)
        fieldslist = fields.split(',')

        sql = "select %s from %s" % (fields, table)
        logfile.info('sql:', sql)
        newret = self.query(self.newdb, sql)
        oldret = self.query(self.olddb, sql)
        # newstr, oldstr
        retstr = ['', '']
        #for res in [newret, oldret]:
        rets = [newret, oldret]
        for i in range(0, len(rets)):
            res = rets[i]
            if res:
                row = res[0]
                xs = []
                for ii in range(0, len(row)):
                    f = row[ii]
                    if type(f) == types.UnicodeType:
                        f = f.encode('utf-8')
                    xs.append(str(f))
                #print 'xs:', xs, fsep.join(xs), retstr, retstr[0], retstr[1], i, type(i)
                retstr[i] = self.fsep.join(xs)


        #if rets[0] != rets[1]: 
        #    logfile.info('diff:', rets)
        if rets[0] != rets[1]:
            return rets[0], rets[1]
        return '', ''


def test():
    import pprint

    db1 = "1.db"
    db2 = "2.db"
    
    logfile.install("stdout")
    x = DBDiff(None, db1, db2)
    ret = x.diff()

    pprint.pprint(ret)

if __name__ == '__main__':
    test()


