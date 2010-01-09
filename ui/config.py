# coding: utf-8
import os, sys
import locale

cf = None

class Configure:
    def __init__(self):
        self.rundir = os.path.dirname(os.path.abspath(sys.argv[0]))
        datadir = os.path.join(self.rundir, 'data')
        if not os.path.isdir(datadir):
            os.mkdir(datadir)
        self.conffile = os.path.join(self.rundir, "data", "youmoney.conf") 
        self.default_lang = 'zh_CN'
        self.lang = locale.getdefaultlocale()[0]
        if not self.lang:
            self.lang = self.default_lang
            try:
                langstr = os.environ['LANG']
            except:
                pass
            else:
                parts = langstr.split('.')
                if len(parts) == 2:
                    self.lang = parts[0]

        self.data = {}
        self.load()

    def load(self):
        try:
            f = open(self.conffile, 'r')
        except:
            self.data['lastdb'] = os.path.join(os.path.dirname(self.conffile), "youmoney.db")
            self.data['lang'] = self.lang
            self.dump()
            return
        lines = f.readlines()
        f.close()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = [ x.strip() for x in line.split('=') ]
            self.data[parts[0]] = parts[1]

        if not self.data.has_key('lang'):
            self.data['lang'] = self.lang

    def dump(self):
        f = open(self.conffile, 'w')
        for k in self.data:
            f.write('%s = %s\n' % (k, self.data[k]))

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


