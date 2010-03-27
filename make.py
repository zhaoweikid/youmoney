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
    os.rename('youmoney.app', 'YouMoney.app')
    os.chdir('../')
    shutil.copy('README.rtf', 'dist')
    
    volname = 'YouMoney-macosx10.5-%s' % (version.VERSION)
    if os.path.isdir(volname):
        shutil.rmtree(volname)

    os.rename('dist', volname)

    newname = 'YouMoney-macosx10.5-%s.dmg' % (version.VERSION)
    if os.path.isfile(newname):
        os.remove(newname)
    cmd = 'hdiutil create -megabytes 50 -volname "%s" -format UDIF -srcfolder "%s" "%s"' % (volname, volname, newname)
    if os.system(cmd) != 0:
        print 'create dmg error!'
        return
 
    filename = 'YouMoney-macosx10.5-%s.dmg.zip' % (version.VERSION)
    if os.path.isfile(filename):
        os.remove(filename)
    z = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    z.write(newname)
    z.close() 


def src_main():
    if os.path.isdir('youmoney'):
        shutil.rmtree('youmoney')

    cmd = 'hg clone https://youmoney.googlecode.com/hg/ youmoney'
    os.system(cmd)
    os.rename('youmoney', 'YouMoney-src-%s' % (version.VERSION))


def debian_main():
    cmd = "rm -rf ../youmoney_*"
    os.system(cmd)

    cmd = 'rm -rf debian/youmoney'
    os.system(cmd)

    f = open('debian/files', 'w')
    s = 'youmoney_%s-1_i386.deb Office extra' % (version.VERSION)
    print s
    f.write(s)
    f.close()
    
    f = open('debian/changelog', 'r')
    lines = f.readlines()
    f.close()

    f = open('debian/changelog', 'w')
    s = 'youmoney (%s-1) unstable; urgency=low\n' % (version.VERSION)
    f.write(s)
    for line in lines[1:]:
        f.write(line)
    f.close() 

    cmd = 'dpkg-buildpackage -rfakeroot'
    os.system(cmd)

def rpm_main():
    os.path.insert(0, 'rpm')
    import  make
    os.chdir('rpm')
    make.main()


if __name__ == '__main__':
    if sys.platform == 'darwin':
        mac_main()
    elif sys.platform.startswith('win32'):
        win32_main()
        src_main()
    elif sys.platform.startswith('linux'):
        f = open('/etc/issue', 'r')
        line = f.readline()
        f.close()

        if line.find('Ubuntu') >= 0:
            debian_main()
        else:
            rpm_main()
    
