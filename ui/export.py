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
        sql = "select * from category"
        rets = self.db.query(sql)
        
        if not rets:
            return None

        cate1 = {}
        for row in rets:
            if row['parent'] == 0:
                cate1[row['id']] = row['name']
        
        rec = [[_('Main Category'), _('Sub Category'), _('Type')]]
        typecn = {}
        for row in rets:
            if row['parent'] != 0:
                rec.append([cate1[row['parent']].encode(self.charset), 
                            row['name'].encode(self.charset), 
                            catetypes[row['type']].encode(self.charset)]) 

        of = open(filename, 'w')
        wt = csv.writer(of)
        for x in rec:
            wt.writerow(x)
        of.close()

    def itemdata(self, filename):
        sql = "select * from category"
        rets = self.db.query(sql)
        if not rets:
            return None
        
        cates = {}
        for row in rets:
            cates[row['id']] = row['name']

        sql = "select * from capital order by year,month,day"
        rets = self.db.query(sql)
        if not rets:
            return None
        
        rec = [[_('Category'), _('Money'), _('Payway'), _('Type'), _('Time'), _('Year'), _('Month'), _('Day')]]
        one = rec[0]
        for i in range(0, len(one)):
            item = one[i]
            if type(item) == types.UnicodeType:
                one[i] = item.encode(self.charset)

        for row in rets:
            tm = datetime.datetime.fromtimestamp(row['ctime']).strftime('%Y-%m-%d')
            pw = row['payway']
            if pw == 0:
                pw = 1
            rec.append([cates[row['category']].encode(self.charset), 
                        row['num'], 
                        payways[pw].encode(self.charset), 
                        catetypes[row['type']].encode(self.charset), 
                        tm, 
                        row['year'], row['month'], row['day']])

        of = open(filename, 'w')
        wt = csv.writer(of)
        for x in rec:
            wt.writerow(x)
        of.close()


class DataImport:
    def __init__(self, db, charset='utf-8'):
        self.db = db
        self.charset = charset

    def category(self, filename):
        pass

    def itemdata(self, filename):
        pass




