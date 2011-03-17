# coding: utf-8
import os, sys
import urlparse, time
import hashlib, binascii
import wx
import urllib, urllib2, traceback
import httplib, mimetypes
import storage, config, rsa, logfile
import base64, json, pickle, zlib, socket
import config
import logfile, storage, netreq
 
def sumfile(filename):
    m = hashlib.md5()
    fobj = open(filename, 'rb')
    while True:
        d = fobj.read(8086)
        if not d:
            break
        m.update(d)
    fobj.close()
    return m.hexdigest()

def sumdata(data):
    m = hashlib.md5()
    start = 0
    while True:
        d = data[start: start+8086]
        if not d:
            break
        m.update(d)
        start += 8086
    return m.hexdigest()


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
        
        f = open(self.conf['lastdb'], 'rb')
        s = f.read()
        f.close()

        self.endata   = zlib.compress(s)
        self.md5val   = sumdata(self.endata)

        self.status   = 0
        self.reqconn  = netreq.Request()

    def auth(self):
        req = {'act':'auth', 'username':self.conf['user'], 'password':self.conf['password']}
        header, data = self.reqconn.docmd(req)
        
        if header['ret'] == 1:
            return True
        return False
        
    def query(self):
        req = {'act':'query', 
               'id':self.conf['id'],
               'ver':self.conf['sync_ver'], 
               'md5':self.md5val}
        
        header, data = self.reqconn.docmd(req)
        logfile.info('query resp:', header, data)
        self.status = header['status']
        return header

    def add_db(self):
        confpath = os.path.join(self.conf.home, 'data', 'youmoney.conf')

        if self.status == self.ADD or self.status == self.COMMIT:
            req = {'act':'upload', 'id':self.conf['id']}

            dbpath = self.conf['lastdb']
            f = open(dbpath, 'rb')
            s = f.read()
            f.close()
            
            #req['md5'] = sumdata(s)
            req['md5'] = self.md5val
            s = zlib.compress(s)
            req['crc32'] = binascii.crc32(s)
            logfile.info('add/commit:', req, 'data:', len(s))
            header, data = self.reqconn.docmd(req, s)
            return header
        
        return {'ret':-2, 'error':'add status error:' + str(self.status)}

    def update_db(self):
        confpath = os.path.join(self.conf.home, 'data', 'youmoney.conf')
 
        if self.status == self.UPDATE:
            req = {'act':'getdata', 'id':self.conf['id']}
            header, data = self.reqconn.docmd(req)
            logfile.info('getdata header:', header, 'data len:', len(data)) 
            
            if data and header.has_key('crc32'):
                v1 = binascii.crc32(data)
                if v1 != header['crc32']:
                    logfile.info('crc32 error! local:', v1, 'server:', header['crc32'])
                    header['ret'] = -1
                    header['error'] = 'crc32 error'
                    return header
            
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

            return header
        
        return {'ret':-2, 'error':'update status error:' + str(self.status)}
        
    def sync_db(self):
        if self.status == self.ADD or self.status == self.COMMIT:
            return self.add_db()
        elif self.status == self.UPDATE:
            return self.update_db()
        

def do_sync(conf, db_sync_first_time, win, onlyci):
    datasync = DataSync(conf)
    if not datasync.auth():
        wx.MessageBox(_('Sync auth error, please check your password for sync.'), _('Sync Information'), wx.OK|wx.ICON_INFORMATION)
        return False

    resp = datasync.query()
    logfile.info('resp:', resp)
    status = resp['status']

    if resp['ret'] != 1:
        wx.MessageBox(resp['error'], _('Sync Information'), wx.OK|wx.ICON_INFORMATION)
        return

    if onlyci:
        if status == DataSync.COMMIT or status == DataSync.ADD:
            ret3 = datasync.add_db()
            logfile.info('sync_db:', ret3)
            if ret3['ret'] == 1:
                conf['sync_ver'] = str(ret3['ver'])
                conf['sync_md5'] = ret3['md5'] 
                conf.dump()
     
        return 

    logfile.info('datasync status:', status)

    if status == DataSync.CONFLICT:
        dlg2 = wx.MessageDialog(win, _('Your data modified in old version. Click YES to cancel modify and use the new version on server. No to use current local data.') + '\n' + _('Server Last Modify') + ': %d-%02d-%02d %02d:%02d:%02d' % time.localtime(resp['time'])[:6], 
                _('Sync Data Conflict'), wx.YES_NO | wx.NO_DEFAULT| wx.ICON_INFORMATION)
        ret2 = dlg2.ShowModal()
        if ret2 == wx.ID_YES:
            status = datasync.status = DataSync.UPDATE
        elif ret2 == wx.ID_NO:
            status = datasync.status = DataSync.COMMIT
        dlg2.Destroy()
                        
    # maybe first sync
    if db_sync_first_time == 0 and resp['ver']:
        status = DataSync.UPDATE
 
    if status == DataSync.ADD or \
       status == DataSync.COMMIT:
        ret3 = datasync.add_db()
        logfile.info('add_db:', ret3)
        if ret3['ret'] == 1:
            conf['sync_ver'] = str(ret3['ver'])
            conf['sync_md5'] = ret3['md5']
            conf.dump()
    
            wx.MessageBox(_('Sync complete!'), 
                          _('Sync Information'), wx.OK|wx.ICON_INFORMATION)
            return True
        else:
            wx.MessageBox(ret3['error'], _('Sync Information'), wx.OK|wx.ICON_INFORMATION)

    elif status == DataSync.UPDATE:
        ret3 = datasync.update_db()
        logfile.info('update_db:', ret3)
        if ret3['ret'] == 1:
            conf['sync_ver'] = str(ret3['ver'])
            conf['sync_md5'] = ret3['md5']
            conf.dump()
            
            return True
        else:
            wx.MessageBox(ret3['error'], _('Sync Information'), wx.OK|wx.ICON_INFORMATION)

    elif status == DataSync.NOUPDATE:
        wx.MessageBox(_('Not need sync!'), 
                      _('Sync Information'), wx.OK|wx.ICON_INFORMATION)
        return False

    return False

def synchronization(win, onlyci=False):
    conf = win.conf
    dbx = datamodel.VerinfoData(win.db)   

    db_sync_first_time = dbx.first_time()
    #sql = "select sync_first_time from verinfo"
    #db_sync_first_time = win.db.query_one(sql)
    logfile.info("db sync first time:", db_sync_first_time)

    win.db.close()
    status = None
    try:
        status = do_sync(win.conf, db_sync_first_time, win, onlyci)
    except Exception, e:
        logfile.info(traceback.format_exc())
        if not onlyci:
            wx.MessageBox(str(e), _('Sync Information'), wx.OK|wx.ICON_INFORMATION)
    finally:
        win.db = storage.DBStorage(win.conf['lastdb'])
        logfile.info('check update sync_first_time:', db_sync_first_time, status)
        if db_sync_first_time == 0 and \
           (status == DataSync.UPDATE or status == DataSync.COMMIT or status == DataSync.ADD):
            dbx.up_first_time()
            #sql = "update verinfo set sync_first_time=%d" % int(time.time())
            #win.db.execute(sql)

    return True 


 



