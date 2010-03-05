# coding: utf-8
import os, sys
import locale
import types, pprint

cf = None

class Configure:
    def __init__(self, charset='utf-8'):
        self.rundir = os.path.dirname(os.path.abspath(sys.argv[0]))
        print 'rundir:', self.rundir
        self.charset = charset
        self.locallang = locale.getdefaultlocale()[0] 
        self.localcharset = locale.getdefaultlocale()[1] 
        dirname = os.path.join(self.rundir, 'data')
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        if sys.platform.startswith('win32'):
            self.confdir = os.path.join(self.rundir, "data")
        else:
            self.confdir = os.path.join(os.environ['HOME'], '.youmoney')
            if not os.path.isdir(self.confdir):
                os.mkdir(self.confdir)

        self.conffile = os.path.join(self.confdir, "youmoney.conf") 
        self.conffile = unicode(self.conffile, self.localcharset)
        self.iscreate = False
        self.data = {}
        self.load()

    def load(self):
        try:
            f = open(self.conffile, 'r')
        except:
            self.iscreate = True
            self.data['lastdb'] = os.path.join(os.path.dirname(self.conffile), "youmoney.db")
            self.data['lang'] = self.locallang
            self.dump()
            return
        lines = f.readlines()
        f.close()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = [ x.strip() for x in line.split('=') ]
            self.data[parts[0]] = unicode(parts[1], self.charset)

        if not self.data.has_key('lang'):
            self.data['lang'] = self.locallang
        if not self.data.has_key('lastdb'):
            self.data['lastdb'] = os.path.join(os.path.dirname(self.conffile), "youmoney.db")


    def dump(self):
        f = open(self.conffile, 'w')
        for k in self.data:
            v = self.data[k]
            if type(v) == types.UnicodeType:
                v = v.encode(self.charset)
            f.write('%s = %s\n' % (k, v))

        f.close()

    def have(self):
        return os.path.isfile(self.conffile)

    def lastdb_is_default(self):
        if self.data['lastdb'] == os.path.join(self.rundir, 'data', 'youmoney.db'):
            return True
        return False

    def __getitem__(self, k):
        return self.data[k]

    def __setitem__(self, k, v):
        self.data[k] = v

    


