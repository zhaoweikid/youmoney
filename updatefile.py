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
    noinstall = 'YouMoney-noinstall-%s.zip' % (version.VERSION)
    #size = os.path.getsize(filename) 
    noinstall_md5val = sumfile(noinstall) 
 
    src = 'YouMoney-src-%s.zip' % (version.VERSION)
    #size = os.path.getsize(filename) 
    src_md5val = sumfile(src) 
    
    f = open("update.txt", 'w')
    f.write('version\t%s\n' % (version.VERSION))
    f.write('%s\t%s\n' % (noinstall, noinstall_md5val))
    f.write('%s\t%s\n' % (src, src_md5val))
    f.close()


if __name__ == '__main__':
    main()


