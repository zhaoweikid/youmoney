# coding: utf-8
import os, sys
import socket, time
import threading, traceback
import Queue, SocketServer
import wx
import logfile, update, event, version

# task: {'id':xx, 'type':xxx}
taskq = Queue.Queue()

class Task (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                task = taskq.get()
            except:
                continue
            try:
                func = getattr(self, 'do_' + task['type'])
            except:
                logfile.info('unkown type')
                continue

            func(task)

    def do_update(self, task):
        update.check(task['frame'])

    
    def do_alert(self, task):
        evt = event.MyAlertEvent(message=task['message'], name='alert')
        wx.PostEvent(task['frame'], evt)

class MyRequest (SocketServer.StreamRequestHandler):
    def handle(self):
        try:
            self.do_handle()
        except:
            logfile.info(traceback.format_exc())

    def do_handle(self):
        self.wfile.write('YouMoney %s\r\n' % (version.VERSION))
        self.wfile.flush()
        line = self.rfile.readline().strip()
       
        if line == 'update':
            msg = _('New package download complete! Update youmoney must close first. Click OK to close YouMoney.')
            evt = event.MyAlertEvent(message=msg, name='update')
            wx.PostEvent(self.server.frame, evt)

        elif line.startswith('message:'):
            evt = event.MyAlertEvent(message=line[line.find(':')+1:], name='alert')
            wx.PostEvent(self.server.frame, evt)
            
        self.wfile.write('ok\r\n')
        self.wfile.flush()
        
class MyServer (SocketServer.TCPServer):
    def __init__(self, frame):
        self.frame = frame
        SocketServer.TCPServer.__init__(self, ('127.0.0.1', 9596), MyRequest)

def start_server(frame):
    svr = MyServer(frame)
    svr.serve_forever()




