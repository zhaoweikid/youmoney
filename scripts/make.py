# coding: utf-8
import os, sys, datetime, shutil
import random
import merge

dstnames = ['youmoney_zh_CN', 'youmoney_ja_JP']

def create_po():
    tm = datetime.datetime.now()
    postfix = '%s%02d%02d.%02d%02d%02d' % tuple(tm.timetuple())[:6]

    home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    os.chdir(os.path.join(home, 'scripts'))

    cmd = "python %s %s" % ('pygettext.py', os.path.join(home, 'ui', '*.py'))
    print cmd
    os.system(cmd)

    cmd = 'move messages.pot youmoney.pot'
    print cmd
    shutil.move('messages.pot', 'youmoney.pot')
    
    #dstnames = ['youmoney_zh_CN', 'youmoney_ja_JP']
    global dstnames 
    for name in dstnames:
        dstfile = name + '.po'
        print dstfile
        # backup old file
        if os.path.isfile(dstfile):
            shutil.move(dstfile, '%s.%s.%d' % (dstfile, postfix, random.randint(0, 10000)))

        merge.merge(name + '.sample', "youmoney.pot", dstfile)

def create_mo():
    global dstnames

    for name in dstnames:
        parts = name.split('_', 1)

        cmd = "python %s %s" % ('msgfmt.py', name)
        print cmd
        os.system(cmd)
        dirname = '../lang/%s/LC_MESSAGES/' % (parts[1])
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        cmd = "copy %s.mo ../lang/%s/LC_MESSAGES/youmoney.mo" % (name, parts[1])
        print cmd
        shutil.copyfile(name + '.mo', '../lang/%s/LC_MESSAGES/youmoney.mo' % (parts[1]))

def create_en():
    home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    os.chdir(os.path.join(home, 'scripts'))
    cmd = "python %s %s" % ('pygettext.py', os.path.join(home, 'ui', '*.py'))
    print cmd
    os.system(cmd)
    
    pofile = 'youmoney_en_US.po'
    cmd = 'move messages.pot ' + pofile
    print cmd
    os.system(cmd)

    f = open(pofile, 'r')
    s = f.read()
    f.close()

    s = s.replace('charset=CHARSET', 'charset=utf-8')

    f = open(pofile, 'w')
    f.write(s)
    f.close()

    cmd = "python %s %s" % ('msgfmt.py', 'youmoney_en_US')
    print cmd
    os.system(cmd)


    cmd = "copy youmoney_en_US.mo ../lang/en_US/LC_MESSAGES/youmoney.mo"
    print cmd
    if not os.path.isdir('../lang/en_US/LC_MESSAGES/'):
        os.makedirs('../lang/en_US/LC_MESSAGES')
    shutil.copyfile('youmoney_en_US.mo', '../lang/en_US/LC_MESSAGES/youmoney.mo')




    
if __name__ == '__main__':
    try:
        action = sys.argv[1]
    except:
        action = 'all'
        
    if action == 'all':
        create_po()
        create_mo()
    elif action == 'mo':
        create_mo()
    elif action == 'po':
        create_po()
    elif action == 'en':
        create_en()


