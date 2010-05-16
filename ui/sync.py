# coding: utf-8
import os, sys
import md5, urlparse
import urllib, urllib2, traceback
import httplib, mimetypes
import storage, config, rsa, logfile
import base64, json, pickle, zlib

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
        
        h = httplib.HTTP(urlparts[1])
        h.putrequest('POST', sel)
        h.putheader('host', host)
        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(data)))
        h.endheaders()
        h.send(data)
        errcode, errmsg, headers = h.getreply()
        return errcode, h.file.read()

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
        self.endata   = zlib.compress(encrypt_file(self.conf['lastdb']))
        self.md5val   = sumdata(self.endata)
        self.url      = self.baseurl + '?action=%s&ident=%s'+'&ver=%s&md5=%s' % (self.conf['sync_ver'], self.md5val)
        self.conf_url = self.baseurl + '?action=%s&ident=%s'
        self.user_url = self.baseurl + '?action=%s&user=%s&pass=%s'+'&ver=%s&md5=%s' % (self.conf['sync_ver'], self.md5val)

        # current status
        self.status   = 0
        
    def query(self):
        if self.conf['sync_way'] == 'id':
            url  = self.url % ('query', self.conf['id'])
        else:
            #password = base64.b64decode(self.conf['password'])
            url  = self.user_url % ('query', self.conf['user'], self.conf['password'])

        resp = urllib2.urlopen(url)
        data = resp.read()
        logfile.info('query resp:', data)
        x = json.loads(data)

        if x.has_key('error'):
            return 0, x
       
        if self.conf['sync_way'] == 'user' and self.conf['id'] != x['id']:
            logfile.info('sync_wary: user, id:', self.conf['id'], x['id'])
            logfile.info(self.get_conf())
            self.status = self.ADD
            return self.status, x

        if self.conf['sync_way'] == 'user' and not x['haveconf']:
            self.upload_conf()

        # return x is last version information 
        if x['ver'] == 0 and not x.has_key('error'):
            self.status = self.ADD
            return self.status, x

        if len(self.conf['sync_ver']) > 0:
            localver = int(self.conf['sync_ver'])
        else:
            if x['ver'] > 0:
                self.status = self.UPDATE
                return self.status, x
            else:
                self.status = self.COMMIT
                return self.status, x

        if x['ver'] == localver: # the same version
            if x['md5'] == self.md5val:
                self.status = self.NOUPDATE
            else:
                self.status = self.COMMIT

        elif x['ver'] > localver: # remote version is newer than local
            #if x['modify']:
            #if self.conf['sync_md5'] != self.md5val: # local modified
            if x['modify']:
                self.status = self.CONFLICT
            else:
                self.status = self.UPDATE
        else:
            self.status = self.ERROR

        return self.status, x

    def query_local(self):
        if len(self.conf['sync_ver']) > 0:
            localver = int(self.conf['sync_ver'])
        else:
            self.status = self.ADD
            return self.status

        if self.conf['sync_md5'] == self.md5val:
            self.status = self.NOUPDATE
        else:
            self.status = self.COMMIT

        return self.status
        

    def sync_db(self):
        confpath = os.path.join(self.conf.home, 'data', 'youmoney.conf')

        if self.status == self.ADD or self.status == self.COMMIT:
            url = self.url % ('upload', self.conf['id'])
            fp = FilePost(url)
            fp.add_data('youmoney.db', 'youmoney.db', self.endata, True)

            errcode, ret = fp.post()
            if errcode >= 200 and errcode < 300:
                return json.loads(ret)

        elif self.status == self.UPDATE:
            url = self.url % ('getdata', self.conf['id'])
            resp = urllib2.urlopen(url)
            data = resp.read()
            
            real = decrypt_data(zlib.decompress(data))
            
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

