# coding: utf-8
import os, sys
import csv, datetime, time, types
import storage
from storage import catetypes, payways

class DataExport:
    def __init__(self, db, charset='utf-8'):
        self.db = db
        self.charset = charset

    def category(self, filename):
        sql = "select * from category order by parent"
        rets = self.db.query(sql)
        
        if not rets:
            raise ValueError, 'No category.'

        cate1 = {}
        subs  = {}

        for row in rets:
            if row['parent'] == 0:
                cate1[row['id']] = row['name']
            else:
                if row['parent'] in subs:
                    subs[row['parent']] += 1
                else:
                    subs[row['parent']] = 1

        rec = [[_('Main Category'), _('Sub Category'), _('Type')]]
        one = rec[0]
        for i in range(0, len(one)):
            item = one[i]
            if type(item) == types.UnicodeType:
                one[i] = item.encode(self.charset)

        typecn = {}
        for row in rets:
            if row['parent'] != 0:
                rec.append([cate1[row['parent']].encode(self.charset), 
                            row['name'].encode(self.charset), 
                            catetypes[row['type']].encode(self.charset)]) 
            else:
                if row['id'] not in subs:
                    rec.append([row['name'].encode(self.charset), 
                            '', 
                            catetypes[row['type']].encode(self.charset)]) 
 
        of = open(filename, 'w')
        wt = csv.writer(of, lineterminator='\n')
        for x in rec:
            wt.writerow(x)
        of.close()

    def itemdata(self, filename):
        sql = "select * from category"
        rets = self.db.query(sql)
        if not rets:
            raise ValueError, 'No category.'
        
        cates = {}
        for row in rets:
            cates[row['id']] = row['name']
        parents = {}
        for row in rets:
            if row['parent'] > 0:
                parents[row['id']] = row['parent']

        sql = "select * from capital order by year,month,day"
        rets = self.db.query(sql)
        if not rets:
            raise ValueError, 'No record.'
        
        rec = [[_('Main Category'), _('Sub Category'), _('Money'), _('Payway'), _('Type'), _('Time'), _('Year'), _('Month'), _('Day'), _('Explain')]]
        one = rec[0]
        for i in range(0, len(one)):
            item = one[i]
            if type(item) == types.UnicodeType:
                one[i] = item.encode(self.charset)

        for row in rets:
            tm = datetime.datetime.fromtimestamp(row['ctime']).strftime('%Y-%m-%d %H:%M:%S')
            pw = row['payway']
            if pw == 0:
                pw = 1
            scate = cates[row['category']].encode(self.charset)
            pcate = scate
            if parents.has_key(row['category']):
                pcate = cates[parents[row['category']]].encode(self.charset)
            else:
                scate = ''

            rec.append([pcate, 
                        scate,
                        row['num'], 
                        payways[pw].encode(self.charset), 
                        catetypes[row['type']].encode(self.charset), 
                        tm, 
                        row['year'], row['month'], row['day'],
                        row['explain'].encode(self.charset)
                        ])

        of = open(filename, 'w')
        wt = csv.writer(of, lineterminator='\n')
        for x in rec:
            wt.writerow(x)
        of.close()
        

class DataImport:
    def __init__(self, db, charset='utf-8'):
        self.db = db
        self.charset = charset

    def category(self, filename):
        f = open(filename, 'r')
        wt = csv.reader(f)
        recs = []
        for maincate,subcate,typen in wt:
            #print maincate,subcate,typen
            recs.append([unicode(maincate, self.charset), 
                         unicode(subcate, self.charset),
                         unicode(typen, self.charset)])
        f.close()
        
        sql = "select * from category order by parent"
        rets = self.db.query(sql)
        
        parents = {}
        parent_id2name = {}
        subs = {}
        for row in rets:
            k = row['name']+'_'+str(row['type'])
            if row['parent'] == 0:
                parents[k] = row['id']
                parent_id2name[row['id']] = row['name']
            else:
                pname = parent_id2name[row['parent']] 
                k1 = row['name'] + '_' + pname + '_' + str(row['type'])
                subs[k1] = row['id']

        for i in range(1, len(recs)):
            x = recs[i]
            tid = catetypes[x[2]]
            k  = x[0] + '_' + str(tid)
            name = x[1].encode('utf-8')

            if parents.has_key(k): # have parent
                pid = parents[k]
            else:
                x0 = x[0].encode('utf-8')
                sql = "insert into category (name,parent,type) values (?,0,?)"
                self.db.execute_param(sql, (x[0].encode('utf-8'), tid,))
                sql = "select id from category where name='%s' and type=%d" % (x0, tid)
                pid = self.db.query_one(sql)
                kn = x[0] + '_' + str(tid)
                parents[kn] = pid
                parent_id2name[pid] = x[0]
            sk = x[0] + '_' + x[1] + '_' + str(tid) 
            if not x[1] or sk in subs:
                continue
            sql = "insert into category (name,parent,type) values (?,?,?)"
            self.db.execute_param(sql, (name, pid, tid,))
            # value is not important
            subs[sk] = 0

    def itemdata(self, filename, callback=None):
        f = open(filename, 'r')
        wt = csv.reader(f)
        recs = []
        wt.next()
        for maincate,subcate,money,payway,type,ctime,year,month,day,explain in wt:
            recs.append([unicode(maincate, self.charset), 
                         unicode(subcate, self.charset),
                         float(money),
                         unicode(payway, self.charset),
                         unicode(type, self.charset),
                         int(time.mktime(time.strptime(ctime, '%Y-%m-%d %H:%M:%S'))),
                         int(year),
                         int(month),
                         int(day),
                         unicode(explain, self.charset)
                         ])
        f.close()

        allnum = len(recs)
        sql = "select * from category order by parent"
        rets = self.db.query(sql)
        
        parents = {}
        parent_id2name = {}
        subs = {}
        for row in rets:
            k = row['name']+'_'+str(row['type'])
            if row['parent'] == 0:
                parents[k] = row['id']
                parent_id2name[row['id']] = row['name']
            else:
                pname = parent_id2name[row['parent']] 
                k1 = row['name'] + '_' + pname + '_' + str(row['type'])
                subs[k1] = row['id']

        for i in range(1, len(recs)):
            x = recs[i]
            tid = catetypes[x[4]]
            k  = x[0] + '_' + str(tid)
            name = x[1].encode('utf-8')

            if parents.has_key(k): # have parent
                pid = parents[k]
            else:
                x0 = x[0].encode('utf-8')
                sql = "insert into category (name,parent,type) values (?,0,?)"
                self.db.execute_param(sql, (x[0].encode('utf-8'), tid,))
                sql = "select id from category where name='%s' and type=%d" % (x0, tid)
                pid = self.db.query_one(sql)
                kn = x[0] + '_' + str(tid)
                parents[kn] = pid
                parent_id2name[pid] = x[0]
            sk = x[0] + '_' + x[1] + '_' + str(tid) 
            cateid = pid
            if x[1]:
                if sk in subs:
                    cateid = subs[sk]
                else:
                    sql = "insert into category (name,parent,type) values (?,?,?)"
                    self.db.execute_param(sql, (name, pid, tid,))
                    sql = "select id from category where name='%s' and parent=%d and type=%d" % (name, pid, tid) 
                    cateid = self.db.query_one(sql)
                    subs[sk] = cateid

            sql = "insert into capital(category,num,ctime,year,month,day,payway,explain,type) values (?,?,?,?,?,?,?,?,?)"
            param = (cateid, x[2], x[5], x[6], x[7], x[8], payways[x[3]], x[9].encode('utf-8'), catetypes[x[4]])
            self.db.execute_param(sql, param)

            callback.Update(int(float(i)/allnum * 100))        







