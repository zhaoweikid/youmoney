# coding: utf-8
import os, sys
import gettext

def install(localdir, languages):
    gettext.translation('youmoney', localedir=localdir, languages=languages).install(True)


def test():
    install("../lang", ['zh_CN'])

    print _("hello")
    print _("me")

if __name__ == '__main__':
    test()



