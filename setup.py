# coding: utf-8
import os, sys
import py2exe, glob
from distutils.core import setup
import version

includes = ['encodings', 'encodings.*', 'gettext', 'glob', 
            'wx.lib.sized_controls', 'wx.gizmos', 'wx.html',
            'sqlite3', 'shutil', 'pprint']
options  = {'py2exe': {
                'compressed': 0,
                'optimize': 2,
                'includes': includes,
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
                  ('ui', glob.glob('ui/*.py')),
                  ('.', [os.path.join(os.environ['SystemRoot'], 'system32', 'msvcp71.dll')]),
                  ],
    options = options,
    windows = [{'script': 'youmoney.pyw', 
                'icon_resources': [(1, 'images/youmoney.ico')]}]
)

