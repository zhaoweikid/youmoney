# coding: utf-8
import os, sys
import sqlite3

class DBDiff:
    def __init__(self, olddbfile, newdbfile):
        self.olddbfile = olddbfile
        self.newdbfile = newdbfile
        
        self.olddb = sqlite3.connect(olddbfile)
        self.newdb = sqlite3.connect(newdbfile)

    def close(self):
        if self.olddb:
            self.olddb.close()
            self.olddb = None
        if self.newdb:
            self.newdb.close()
            self.newdb = None

    def diff(self):
        tables = ['category', 'capital', 'user' ,'identity', 'verinfo', 'recycle']

        for tbl in tables:
            self.table_diff(tbl)



    def table_diff(self, table):
        pass




