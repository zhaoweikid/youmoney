# coding: utf-8
import os, sys
import md5, urlparse, time
import wx
import urllib, urllib2, traceback
import httplib, mimetypes
import storage, config, rsa, logfile
import base64, json, pickle, zlib, socket
import logfile, storage
 
socket.setdefaulttimeout(10)

def sumfile(filename):
    m = md5.new()
    fobj = open(filename, 'rb')
    while True:
        d = fobj.read(8086)
        if not d:
            break
        m.update(d)
    fobj.close()
    return m.hexdigest()

def sumdata(data):
    m = md5.new()
    start = 0
    while True:
        d = data[start: start+8086]
        if not d:
            break
        m.update(d)
        start += 8086
    return m.hexdigest()
'''
def encrypt_file(filename):
    f = open(filename, 'rb')
    s = f.read()
    f.close()
    
    r = config.cf['rsa_pub']
    eqnum = len(r) % 4
    r += '='*eqnum

    rsa_pub = pickle.loads(base64.b64decode(r))
    s = base64.b64encode(s)
    data = rsa.encrypt(s, rsa_pub)

    return data

def decrypt_data(data):
    s = config.cf['rsa_private']
    eqnum = len(s) % 4
    s += '='*eqnum
    rsa_pri = pickle.loads(base64.b64decode(s))
    return base64.b64decode(rsa.decrypt(data, rsa_pri))
'''   

class MyHTTP(httplib.HTTP):
    _http_vsn = 11
    _http_vsn_str = 'HTTP/1.1'

class FilePost:
    BOUNDARY = '------------tHiS_Is_My_BoNdArY_'
    CRLF = '\r\n'

    def __init__(self, url):
        self.url  = url
        #self.name = name
        #self.filename = 'youmoney.db'
        self.data = []

    def post(self):
        itemlist = []
        for item in self.data:
            body = self.encode_body(item[0], item[1], item[2])
            itemlist.append(body)
        itemlist.append('--' + self.BOUNDARY + '--') 
        
        data = ''.join(itemlist)

        content_type = 'multipart/form-data; boundary="%s"' % self.BOUNDARY
        urlparts = urlparse.urlsplit(self.url) 
        host = urlparts[1]
        sel = self.url[self.url.find(host) + len(host):]
        
        #h = httplib.HTTP(urlparts[1])
        h = MyHTTP(urlparts[1])
        h.putrequest('POST', sel)
        h.putheader('host', host)
        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(data)))
        h.endheaders()
        h.send(data)
        errcode, errmsg, headers = h.getreply()
        return errcode, h.getfile().read()

    def add_file(self, name, filename, iszip=False):
        f = open(filename, 'rb')
        data = f.read()
        f.close()
        self.data.append([name, filename, zlib.compress(data)])

    def add_data(self, name, filename, data, datacompress=False):
        if not datacompress:
            self.data.append([name, filename, zlib.compress(data)])
        else:
            self.data.append([name, filename, data])

    def encode_body(self, name, filename, data):
        lines = [] 

        lines.append('--' + self.BOUNDARY)
        lines.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (name, filename))
        lines.append('Content-Type: application/octet-stream')
        lines.append('')
        lines.append(data)
        #lines.append('--' + self.BOUNDARY + '--')
        lines.append('')

        return self.CRLF.join(lines)



class DataSync:
    NOUPDATE = 1  # not update
    COMMIT   = 2  # local must commit
    UPDATE   = 3  # local must update
    CONFLICT = 4  # local conflict with remote
    ERROR    = 5  # version error
    ADD      = 6  # must add

    def __init__(self, cf):
        self.conf     = cf
        self.path     = cf['lastdb']
        #self.baseurl  = 'http://youmoney.pythonid.com/sync'
        self.baseurl  = 'http://%s/sync' % (self.conf['server'])
        
        f = open(self.conf['lastdb'], 'rb')
        s = f.read()
        f.close()

        self.endata   = zlib.compress(s)

        self.md5val   = sumdata(self.endata)
        self.url      = self.baseurl + '?action=%s&ident=%s'+'&ver=%s&md5=%s' % (self.conf['sync_ver'], self.md5val)
        self.conf_url = self.baseurl + '?action=%s&ident=%s'
        self.user_url = self.baseurl + '?action=%s&user=%s&pass=%s'+'&ver=%s&md5=%s' % (self.conf['sync_ver'], self.md5val)

        # current status
        self.status   = 0
        
    def query(self):
        url  = self.user_url % ('query', self.conf['user'], self.conf['password'])

        resp = urllib2.urlopen(url)
        data = resp.read()
        logfile.info('query resp:', data)
        x = json.loads(data)

        if x.has_key('error'):
            return 0, x
       
        if self.conf['sync_way'] == 'user' and self.conf['id'] != x['id']:
            logfile.info('sync_way: user, local id:', self.conf['id'], 'remote id:', x['id'])
            self.conf['id'] =  x['id']
            self.conf.dump()
            #logfile.info(self.get_conf())
            self.status = self.ADD
            return self.status, x

        #if self.conf['sync_way'] == 'user' and not x['haveconf']:
        #    self.upload_conf()

        # return x is last version information 
        if x['ver'] == 0 and not x.has_key('error'):
            self.status = self.ADD
            return self.status, x
            
        # get local sync_ver
        if len(self.conf['sync_ver']) > 0:
            localver = int(self.conf['sync_ver'])
        else: # not have local sync_ver
            logfile.info('not found local sync_ver, remote:', x['ver'])
            if x['ver'] > 0: # remove have sync_ver, update
                self.status = self.UPDATE
                return self.status, x
            else: # remote and local both not have sync_ver, ADD
                self.status = self.ADD
                return self.status, x

        if x['ver'] == localver: # the same version
            logfile.info('check md5, local db: ',self.md5val, 'remote:', x['md5'])
            if x['md5'] == self.md5val: # the same md5, not update
                self.status = self.NOUPDATE
            else: # modified, commit
                self.status = self.COMMIT

        elif x['ver'] > localver: # remote version is newer than local
            #if x['modify']:
            #if self.conf['sync_md5'] != self.md5val: # local modified
            if x['modify']: # user modified on old data, conflict
                self.status = self.CONFLICT
            else: # update
                self.status = self.UPDATE
        else:
            self.status = self.ERROR

        return self.status, x

    def sync_db(self):
        confpath = os.path.join(self.conf.home, 'data', 'youmoney.conf')

        if self.status == self.ADD or self.status == self.COMMIT:
            url = self.url % ('upload', self.conf['id'])
            fp = FilePost(url)
            fp.add_data('youmoney.db', 'youmoney.db', self.endata, True)

            errcode, ret = fp.post()
            logfile.info('file post return:', ret)
            if errcode >= 200 and errcode < 300:
                return json.loads(ret)

        elif self.status == self.UPDATE:
            url = self.url % ('getdata', self.conf['id'])
            resp = urllib2.urlopen(url)
            data = resp.read()
            
            logfile.info('getdata len:', len(data)) 
            real = zlib.decompress(data)
            
            lastdb = self.conf['lastdb']
            bakdb  = lastdb + '.bak'

            tmpdb = lastdb + '.tmp'
            f = open(tmpdb, 'wb')
            f.write(real)
            f.close()

            if os.path.isfile(bakdb):
                os.remove(bakdb)
            if os.path.isfile(lastdb):
                os.rename(lastdb, bakdb)
            os.rename(tmpdb, lastdb)

            return True 
        return None


    def upload_conf(self):
        upkeys = ['id', 'user', 'password', 'rsa_private', 'rsa_pub', 'sync_way']
        data = {}

        for k in upkeys:
            data[k] = self.conf[k]

        url = self.conf_url % ('upconf', self.conf['id'])
    
        postdata = urllib.urlencode({'data': json.dumps(data)})
        resp = urllib2.urlopen(url, postdata)
        s = resp.read()
        x = json.loads(s)

        return True

    def get_conf(self):
        if self.conf['sync_way'] != 'user':
            return None

        url  = self.user_url % ('getconf', self.conf['user'], self.conf['password'])

        resp = urllib2.urlopen(url)
        s = resp.read()
         
        data = json.loads(s)
        if not data.has_key('error'):
            logfile.info('get conf:', data['data'])
            self.conf.load_data(data['data'])

        return data 



def do_sync(conf, db_sync_first_time, win, alert):
    datasync = DataSync(conf)
    status, resp = datasync.query()
    logfile.info('status:', status, resp)

    if status == DataSync.CONFLICT:
        dlg2 = wx.MessageDialog(win, _('Your data modified in old version. Click YES to cancel modify and use the new version on server. No to use current local data.') + '\n' + _('Server Last Modify') + ': %d-%02d-%02d %02d:%02d:%02d' % time.localtime(resp['time'])[:6], 
                _('Sync Data Conflict'), wx.YES_NO | wx.NO_DEFAULT| wx.ICON_INFORMATION)
        ret2 = dlg2.ShowModal()
        if ret2 == wx.ID_YES:
            datasync.status = DataSync.UPDATE
        elif ret2 == wx.ID_NO:
            datasync.status = DataSync.COMMIT
        dlg2.Destroy()
    elif status == 0:
        wx.MessageBox(resp['error'], _('Sync Information'), wx.OK|wx.ICON_INFORMATION)
                        
    # maybe first sync
    if db_sync_first_time == 0 and resp['ver']:
        datasync.status = DataSync.UPDATE
 
    #if updateonly and datasync.status != DataSync.UPDATE:
    #    logfile.info('update only return:', datasync.status)
    #    return 0

    logfile.info('datasync status:', datasync.status)                    
    if datasync.status == DataSync.UPDATE or \
       datasync.status == DataSync.ADD or \
       datasync.status == DataSync.COMMIT:
        ret3 = datasync.sync_db()
        logfile.info('sync_db:', ret3)
        if ret3:
            if not ret3 is True: # ADD or COMMIT
                conf['sync_ver'] = str(ret3['ver'])
                conf['sync_md5'] = datasync.md5val
                conf.dump()
            else: # UPDATE
                conf['sync_ver'] = str(resp['ver'])
                conf['sync_md5'] = resp['md5']
                conf.dump()
        
        if alert:
            wx.MessageBox(_('Sync complete!'), 
                      _('Sync Information'), wx.OK|wx.ICON_INFORMATION)
    elif datasync.status == DataSync.NOUPDATE:
        if alert:
            wx.MessageBox(_('Not need sync!'), 
                      _('Sync Information'), wx.OK|wx.ICON_INFORMATION)

    return datasync.status

def synchronization(win, alert=True):
    conf = win.conf
   
    db_sync_first_time = 0
    sql = "select sync_first_time from verinfo"
    db_sync_first_time = win.db.query_one(sql)
    logfile.info("db sync first time:", db_sync_first_time)

    win.db.close()
    status = None
    try:
        status = do_sync(win.conf, db_sync_first_time, win, alert)
    except Exception, e:
        logfile.info(traceback.format_exc())
        wx.MessageBox(str(e), _('Sync Information'), wx.OK|wx.ICON_INFORMATION)
    finally:
        win.db = storage.DBStorage(win.conf['lastdb'])
        logfile.info('check update sync_first_time:', db_sync_first_time, status)
        if db_sync_first_time == 0 and \
           (status == DataSync.UPDATE or status == DataSync.COMMIT or status == DataSync.ADD):
            sql = "update verinfo set sync_first_time=%d" % int(time.time())
            win.db.execute(sql)

 


 



