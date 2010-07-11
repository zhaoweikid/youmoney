# coding: utf-8
import os, sys
import types, datetime
import shutil

logobj = None

class LogFile:
    def __init__(self, filename, charset='utf-8'):
        self.charset = charset
        self.filename = filename
        
        if filename == 'stdout':
            self.file = sys.stdout
        else:
            if os.path.isfile(filename):
                if os.path.getsize(filename) > 1024 * 1024 * 2:
                    bakfile = filename + '.bak'
                    if os.path.isfile(bakfile):
                        os.remove(bakfile)
                    shutil.move(filename, bakfile)
            self.file = open(filename, 'a+')

    def info(self, *s):
        ss = []
        for x in s:
            t = type(x)
            if t == types.UnicodeType:
                ss.append(x.encode(self.charset, 'ignore'))
            elif t == types.StringType:
                ss.append(x)
            else:
                ss.append(str(x))
        self.file.write("%s %s\n" % (str(datetime.datetime.now()), ' '.join(ss)))
        self.file.flush()

    def close(self):
        self.file.close()
        self.file = None


def info(*s):
    logobj.info(*s)

def install(filename, charset='utf-8'):
    global logobj
    logobj = LogFile(filename, charset)


def test():
    install("test.log")
    info('aaa', 'bbbbbbbb')
    info('fdsafasf', ['fasfd', 'ssss'])

if __name__ == '__main__':
    test()


    

