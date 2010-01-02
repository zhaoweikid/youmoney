# coding: utf-8
import os, sys
import py2exe, glob

includes = []
options  = {'py2exe': {
                'compressed': 0,
                'includes': includes,
                'excludes': modules,
                }}


setup(
    version = "0.3",
    description = 'youmoney',
    name = 'YouMoney',
    data_files = [],
    options = options,
    windows = [{'script': 'youmoney.py', 
                'icon_resources': [()]}])
