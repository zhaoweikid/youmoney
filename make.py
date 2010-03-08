# coding: utf-8
import os, sys, shutil, zipfile
import version

def win32_main():
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
    #z = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    #for root,dirs,files in os.walk(newname):
    #    for fname in files:
    #        fpath = os.path.join(root, fname)
    #        z.write(fpath)
    #z.close() 
    
def mac_main():
    if os.path.isdir('dist'):
        shutil.rmtree('dist')
    if os.path.isdir('build'):
        shutil.rmtree('build')

    cmd = "/usr/local/bin/python setup.py py2app"
    if os.system(cmd) != 0:
        print 'setup.py py2app error!'
        return
 
    os.chdir('dist')
    
    volname = 'YouMoney-macosx10.5-%s' % (version.VERSION)
    newname = 'YouMoney-macosx10.5-%s.dmg' % (version.VERSION)
    cmd = 'hdiutil create -megabytes 50 -volname "%s" -format UDIF -srcfolder "youmoney.app" "%s"' % (volname, newname)
    if os.system(cmd) != 0:
        print 'create dmg error!'
        return
 
    filename = 'YouMoney-macosx10.5-%s.dmg.zip' % (version.VERSION)
    z = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    z.write(newname)
    z.close() 
 

if __name__ == '__main__':
    if sys.platform == 'darwin':
        mac_main()
    elif sys.platform.startswith('win32'):
        win32_main()


