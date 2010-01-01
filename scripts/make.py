# coding: utf-8
import os, sys, datetime, shutil
import random
import merge

tm = datetime.datetime.now()
postfix = '%s%02d%02d.%02d%02d%02d' % tuple(tm.timetuple())[:6]

home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.chdir(os.path.join(home, 'scripts'))

cmd = "/usr/bin/python %s %s" % ('pygettext.py', os.path.join(home, 'ui', '*.py'))
print cmd
os.system(cmd)

dstfile = 'youmoney_zh_CN.po'
if os.path.isfile(dstfile):
    shutil.move(dstfile, '%s.%s.%d' % (dstfile, postfix, random.randint(0, 10000)))

cmd = 'mv messages.pot youmoney_zh_CN.pot'
print cmd
os.system(cmd)
merge.merge('youmoney_zh_CN.sample', "youmoney_zh_CN.pot", dstfile)

cmd = "/usr/bin/python %s %s" % ('msgfmt.py', 'youmoney_zh_CN')

print cmd
os.system(cmd)

cmd = "cp youmoney_zh_CN.mo ../lang/zh_CN/LC_MESSAGES/youmoney.mo"
print cmd
os.system(cmd)



