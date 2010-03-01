# coding: utf-8
import os, sys, shutil, zipfile
import version

def main():
    f = open("youmoney.nsi", 'r')
    lines = f.readlines()
    f.close()
    
    f = open("youmoney.nsi.new", 'w')
    for line in lines:
        if line.startswith('OutFile'):
            f.write('OutFile "YouMoney-%s.exe"\n' % (version.VERSION))
        else:
            f.write(line)

    f.close()
    
    if os.path.isfile("youmoney.nsi.bak"):
        os.remove("youmoney.nsi.bak")
    
    shutil.move("youmoney.nsi", "youmoney.nsi.bak")
    shutil.move("youmoney.nsi.new", "youmoney.nsi")
    
    if os.path.isdir('dist'):
        shutil.rmtree('dist')

    cmd = "setup.py py2exe"
    print cmd
    if os.system(cmd) != 0:
        print 'setup.py py2exe error!'
        return
    cmd = "makensis.exe youmoney.nsi"
    print cmd
    os.system(cmd)
    
    shutil.rmtree('build')
    #shutil.rmtree('dist')
    newname = 'YouMoney-noinstall-%s' % (version.VERSION) 
    if os.path.isdir(newname):
        shutil.rmtree(newname)
    shutil.move('dist', newname)
    
    #filename = newname + '.zip'
    #z = zipfile.ZipFile(filename, 'w')
    #for root,dirs,files in os.walk(newname):
    #    for fname in files:
    #        fpath = os.path.join(root, fname)
    #        z.write(fpath)
    #z.close() 

if __name__ == '__main__':
    main()


