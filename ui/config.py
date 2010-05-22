# coding: utf-8
import os, sys
import locale, time, version
import types, pprint, uuid
import base64, pickle
#import rsa

cf = None

class Configure:
    def __init__(self, charset='utf-8'):
        self.rundir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.home = self.rundir
        #print 'rundir:', self.rundir
        self.charset = charset
        self.locallang = locale.getdefaultlocale()[0] 
        if sys.platform == 'darwin':
            if not self.locallang:
                self.localcharset = 'utf-8'
                self.locallang = 'zh_CN'
            else:
                self.localcharset = locale.getdefaultlocale()[1] 
        else:
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
        # is new create db file
        self.iscreate = False
        # sync_way maybe 'user/id'
        self.datadef = {'lastdb':'', 'lang':'', #'rsa_pub':'', 'rsa_private':'', 
                     'id':'', 'user':'', 'password':'', 'sync_way':'id',
                     'sync_ver':'', 'sync_auto': '', 'sync_md5':'', 'server':'youmoney.pythonid.com'}

        self.data = None
        self.load()

    def load(self):
        self.data = {}
        self.data.update(self.datadef)
        try:
            f = open(self.conffile, 'r')
        except:
            self.iscreate = True
            self.data['lastdb'] = os.path.join(os.path.dirname(self.conffile), "youmoney.db")
            self.data['lang'] = self.locallang
            #self.dump()
        else:
            lines = f.readlines()
            f.close()

            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
            
                parts = [ x.strip() for x in line.split('=', 1) ]
                self.data[parts[0]] = unicode(parts[1], self.charset)

        if not self.data.has_key('lang'):
            self.data['lang'] = self.locallang
        if not self.data.has_key('lastdb'):
            self.data['lastdb'] = os.path.join(os.path.dirname(self.conffile), "youmoney.db")

        if not os.path.isfile(self.data['lastdb']):
            self.iscreate = True

        #if not self.data['rsa_pub'] or not self.data['rsa_private']:
        #    keys = rsa.gen_pubpriv_keys(128)
        #    self.data['rsa_pub'] = base64.b64encode(pickle.dumps(keys[0]))
        #    self.data['rsa_private'] = base64.b64encode(pickle.dumps(keys[1]))

        self.dump()

    def reload(self):
        self.iscreate = False
        self.load()

    def load_data(self, data):
        self.data.update(data)
        self.dump()

    def dump(self):
        f = open(self.conffile, 'w')
        keys = self.data.keys()
        keys.sort()
        for k in keys:
            v = self.data[k]
            if type(v) == types.UnicodeType:
                v = v.encode(self.charset)
            f.write('%s = %s\n' % (k, v))

        f.close()

    def have(self):
        return os.path.isfile(self.conffile)

    def default_db_path(self):
        return os.path.join(os.path.dirname(self.conffile), "youmoney.db")

    def lastdb_is_default(self):
        if self.data['lastdb'] == os.path.join(self.rundir, 'data', 'youmoney.db'):
            return True
        return False

    def setid(self, idstr):
        if idstr != self.data['id']:
            self.data['id'] = idstr
            self.dump()

    def __getitem__(self, k):
        return self.data[k]

    def __setitem__(self, k, v):
        self.data[k] = v

    


