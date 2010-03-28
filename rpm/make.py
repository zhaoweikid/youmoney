#!/usr/bin/python
import os, sys

def change_version(filename, ver):
    fr = open(filename, 'r')
    fw = open(filename + '.new', 'w')
        
    for line in fr:
        if line.startswith('Version:'):
            fw.write('Version: %s\n' % (ver))
        else:
            fw.write(line)

    fr.close()
    fw.close()

def main():
    #spechome = os.path.dirname(os.path.abspath(__file__))
    spechome = os.getcwd()
    print 'spechome:', spechome
    home = os.path.dirname(spechome)
    print 'home:', home
    sys.path.insert(0, home)
    import version
    
    change_version("youmoney.spec", version.VERSION)
    if os.path.isfile('youmoney.spec.old'):
        os.remove('youmoney.spec.old')
    os.rename('youmoney.spec', 'youmoney.spec.old')
    os.rename('youmoney.spec.new', 'youmoney.spec')

    dir = os.path.dirname(home)
    #print dir
    os.chdir(dir)
    name = "YouMoney-%s" % (version.VERSION) 
    print 'name:', name
    cmd = "rm -rf " + name
    os.system(cmd)
    
    cmd = "cp -R youmoney " + name
    os.system(cmd)

    cmd = "zip -r %s.zip %s" % (name, name)
    os.system(cmd)

    userhome = os.environ['HOME']
    cmd = "cp %s.zip %s/rpmbuild/SOURCES/" % (name, userhome)
    print cmd
    os.system(cmd)
    
    os.chdir(spechome)
    cmd = "rpmbuild -bb youmoney.spec"
    print cmd
    os.system(cmd)

    files = os.listdir("%s/rpmbuild/RPMS" % (userhome))
    rpmfile = "%s/rpmbuild/RPMS/%s/%s-1.%s.rpm" % (userhome, files[0], name, files[0])
    print rpmfile
    cmd = "cp %s ." % (rpmfile)
    os.system(cmd)


if __name__ == '__main__':
    main()

