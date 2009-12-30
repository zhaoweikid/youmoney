# conding: utf-8
import os, sys
import sqlite3
import base64, pickle

class Dropbox:
    def __init__(self):
        if sys.platform.startswith('win23'):
            userdir = os.environ['USERPROFILE']       
            self.dropboxfile = os.path.join(userdir, "Application Data", "Dropbox", "dropbox.db")
        else:
            userdir = os.path.join(os.environ['HOME'], '.dropbox')
            self.dropboxfile = os.path.join(userdir, "dropbox.db")
        self.load()
      
    def load(self):
        #print 'file:', self.dropboxfile
        self.db = sqlite3.connect(self.dropboxfile)
        sql = "select value from config where key='dropbox_path'"
        cur = self.db.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()
        self.db.close()
        self.db = None
        
        if row:
            self.dropboxdir = pickle.loads(base64.decodestring(row[0]))
        else:
            self.dropboxdir = os.environ['HOME']


    def dir(self):
        return self.dropboxdir


if __name__ == '__main__':
    d = Dropbox()
    print 'dropbox path:', d.dir()


