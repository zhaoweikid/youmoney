# coding: utf-8
import os, sys
import sqlite3, locale
import types, time

# type: 0 支出 1 收入
createtable = ['create table if not exists category (id integer primary key autoincrement, name varchar(64) not null, parent integer default 0, type integer default 0)',
               'create table if not exists capital (id integer primary key autoincrement, category integer, num float, ctime integer, year integer, month integer, day integer, payway integer, explain text, type integer default 0)',
               'create table if not exists user(password varchar(128), mtime integer default 0)']

catetypes = {0:_('Payout'), 1:_('Income'), _('Payout'):0, _('Income'):1}
payways   = {1:_('Cash'), 2:_('Credit Card'), _('Cash'):1, _('Credit Card'):2}


class DBStorage:
    def __init__(self, path):
        self.localcharset = locale.getdefaultlocale()[1]
        self.charset = 'utf-8'
        self.path = path
        if type(path) == types.UnicodeType:
            self.path = path.encode(self.charset)
        self.db = sqlite3.connect(self.path)
        
        self.init()

    def init(self):
        for s in createtable:
            self.execute(s)

        sql = "select * from user"
        ret = self.query(sql, False)
        if not ret:
            sql = "insert into user values ('',%d)" % (int(time.time()))
            self.execute(sql)

    def close(self):
        self.db.close()
        self.db = None

    def execute(self, sql, autocommit=True):
        self.db.execute(sql)
        if autocommit:
            self.db.commit()

    def execute_param(self, sql, param, autocommit=True):
        self.db.execute(sql, param)
        if autocommit:
            self.db.commit()

    def commit(self):
        self.db.commit()
        
    def rollback(self):
        self.db.rollback()

    def query(self, sql, iszip=True):
        if type(sql) == types.UnicodeType:
            sql = sql.encode(self.charset, 'ignore')
 
        cur = self.db.cursor()
        cur.execute(sql)
 
        res = cur.fetchall()
        ret = []

        if res and iszip:
            des = cur.description
            names = [x[0] for x in des]
 
            for line in res:
                ret.append(dict(zip(names, line))) 
        else:
            ret = res 

        cur.close()
        return ret 

    def query_one(self, sql):
        if type(sql) == types.UnicodeType:
            sql = sql.encode(self.charset, 'ignore')
 
        cur = self.db.cursor()
        cur.execute(sql)
        one = cur.fetchone()
        cur.close()
        
        if one:
            return one[0]
        return None

    def last_insert_id(self):
        sql = "select last_insert_rowid()"
        cur = self.db.cursor()
        cur.execute(sql)
        one = cur.fetchone()
        cur.close()

        return one[0]


def test():
    db = DBStorage('test.db')

    db.execute('create table testme(id integer primary key autoincrement, name varchar(256))')
    db.execute("insert into testme(name) values ('zhaowei')")

    print db.query("select * from testme")
    
    db.close()



if __name__ == '__main__':
    test()


  

