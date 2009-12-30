# coding: utf-8
import os, sys
import sqlite3
import types

# type: 0 支出 1 收入
createtable = ['create table if not exists category (id integer primary key autoincrement, name varchar(64) not null, parent integer default 0, type integer default 0)',
               'create table if not exists capital (id integer primary key autoincrement, category integer, num float, ctime integer, year integer, month integer, day integer, payway integer, explain text, type integer default 0)']

class DBStorage:
    def __init__(self, path):
        self.path = path
        self.db = sqlite3.connect(path)
        self.charset = 'utf-8'
        
        self.init()

    def init(self):
        for s in createtable:
            self.execute(s)

    def close(self):
        self.db.close()
        self.db = None

    def execute(self, sql, autocommit=True):
        self.db.execute(sql)
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


def test():
    db = DBStorage('test.db')

    db.execute('create table testme(id integer primary key autoincrement, name varchar(256))')
    db.execute("insert into testme(name) values ('zhaowei')")

    print db.query("select * from testme")
    
    db.close()



if __name__ == '__main__':
    test()


  

