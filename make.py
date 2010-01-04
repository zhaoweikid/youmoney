# coding: utf-8
import os, sys, shutil
import version

def main():
    f = open("youmoney.nsi", 'r')
    lines = f.readlines()
    f.close()
    
    f = open("youmoney.nsi.new", 'w')
    for line in lines:
        if line.startswith('OutFile'):
            f.write('OutFile "YouMoney_%s.exe"\n' % (version.VERSION))
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
    os.system(cmd)
    cmd = "makensis.exe youmoney.nsi"
    print cmd
    os.system(cmd)
    
    shutil.rmtree('build')
    #shutil.rmtree('dist')
    os.rename('dist', 'YouMoney-noinstall-%s' % (version.VERSION))


if __name__ == '__main__':
    main()


