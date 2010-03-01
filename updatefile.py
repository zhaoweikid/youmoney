# coding: utf-8
import os, sys, md5
import version

def sumfile(filename):
    m = md5.new()
    fobj = open(filename, 'r')
    while True:
        d = fobj.read(8086)
        if not d:
            break
        m.update(d)
    fobj.close()
    return m.hexdigest()

def main():
    filename = 'YouMoney-noinstall-%s.zip' % (version.VERSION)
    size = os.path.getsize(filename) 
    md5val = sumfile(filename) 
    
    f = open("update.txt", 'w')
    f.write('version\t%s\n' % (version.VERSION))
    f.write('md5\t%s\n' % (md5val))
    f.write('size\t%d\n' % (size))
    f.close()


if __name__ == '__main__':
    main()


