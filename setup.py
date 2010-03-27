# coding: utf-8
import os, sys
import glob
import version

if sys.platform == 'darwin':
    from setuptools import setup
    setup(app = ["youmoney.py"],
        setup_requires=["py2app"],
        data_files = [('images', glob.glob('images/*.png')),
                  ('lang/zh_CN/LC_MESSAGES', glob.glob('lang/zh_CN/LC_MESSAGES/*')),
                  ('lang/en_US/LC_MESSAGES', glob.glob('lang/en_US/LC_MESSAGES/*')),
                  ('lang/ja_JP/LC_MESSAGES', glob.glob('lang/ja_JP/LC_MESSAGES/*')),
                  ('ui', glob.glob('ui/*.py')),
                  ('data', glob.glob('data/*.csv')),
                  ],
        options=dict(py2app=dict(
            iconfile="images/youmoney.icns",
            ))
 
    )
elif sys.platform.startswith('win32'):
    import py2exe
    from distutils.core import setup
    includes = ['encodings', 'encodings.*', 'gettext', 'glob', 
            'wx.lib.sized_controls', 'wx.gizmos', 'wx.html',
            'wx.lib.wordwrap', 'wx.lib.hyperlink', 'wx.lib.newevent',
            'sqlite3', 'shutil', 'pprint', 'md5', 'urllib',
            'urllib2', 'httplib', 'csv']
    options  = {'py2exe': {
                'compressed': 0,
                'optimize': 2,
                'includes': includes,
                #'bundle_files': 1
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
                  ('data', glob.glob('data/*.csv')),
                  ('.', [os.path.join(os.environ['SystemRoot'], 'system32', 'msvcp71.dll')]),
                  ('.', ['YouMoney.exe.manifest']),
                  ],
        options = options,
        zipfile = None,
        windows = [{'script': 'youmoney.pyw', 
                'icon_resources': [(1, 'images/youmoney.ico')]}]
    )


    setup(version=version.VERSION,
        description = 'YouMoney Updater',
        name = 'Updater',
        author = 'zhaoweikid',
        author_email = 'zhaoweikid@gmail.com',
        url = 'http://code.google.com/p/youomoney/',
        options = options,
        zipfile = None,
        windows = [{'script': 'updater.py'}]
    )

