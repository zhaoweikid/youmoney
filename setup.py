# coding: utf-8
import os, sys
import py2exe, glob
from distutils.core import setup
import version

includes = ['encodings', 'encodings.*', 'gettext', 'glob', 
            'wx.lib.sized_controls', 'wx.gizmos', 'wx.html',
            'wx.lib.wordwrap', 'wx.lib.hyperlink', 'wx.lib.newevent',
            'sqlite3', 'shutil', 'pprint', 'md5', 'urllib',
            'urllib2', 'httplib', 'csv']
options  = {'py2exe': {
                'compressed': 0,
                'optimize': 2,
                'includes': includes,
                'bundle_files': 1
                }}


setup(
    version = version.VERSION,
    description = 'youmoney',
    name = 'YouMoney',
    author = 'zhaoweikid',
    author_email = 'zhaoweikid@gmail.com',
    url = 'http://code.google.com/p/youomoney/',
    data_files = [('images', glob.glob('images/*.png')),
                  ('lang/zh_CN/LC_MESSAGES', glob.glob('lang/zh_CN/LC_MESSAGES/*')),
                  ('lang/en_US/LC_MESSAGES', glob.glob('lang/en_US/LC_MESSAGES/*')),
                  ('lang/ja_JP/LC_MESSAGES', glob.glob('lang/ja_JP/LC_MESSAGES/*')),
                  ('ui', glob.glob('ui/*.py')),
                  ('.', [os.path.join(os.environ['SystemRoot'], 'system32', 'msvcp71.dll')]),
                  ],
    options = options,
    zipfile = None,
    windows = [{'script': 'youmoney.pyw', 
                'icon_resources': [(1, 'images/youmoney.ico')]}]
)

