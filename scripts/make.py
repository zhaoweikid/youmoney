# coding: utf-8
import os, sys, datetime, shutil
import random
import merge


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
    os.system(cmd)

    dstfile = 'youmoney_zh_CN.po'
    if os.path.isfile(dstfile):
        shutil.move(dstfile, '%s.%s.%d' % (dstfile, postfix, random.randint(0, 10000)))

    merge.merge('youmoney_zh_CN.sample', "youmoney.pot", dstfile)

def create_mo():
    cmd = "python %s %s" % ('msgfmt.py', 'youmoney_zh_CN')
    print cmd
    os.system(cmd)

    cmd = "copy youmoney_zh_CN.mo ../lang/zh_CN/LC_MESSAGES/youmoney.mo"
    print cmd
    shutil.copyfile('youmoney_zh_CN.mo', '../lang/zh_CN/LC_MESSAGES/youmoney.mo')

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


