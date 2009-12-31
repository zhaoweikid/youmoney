# coding: utf-8
import os, sys

def merge():
    olddict = {}
    oldf = open("messages.po", 'r')
    while True:
        line = oldf.readline()
        if not line:
            break
        if line.startswith('msgid'):
            idstr = line[5:].strip()
            line2 = oldf.readline()
            vastr = line2[6:].strip()
            olddict[idstr] = vastr
    oldf.close()

    f = open("messages.txt", 'w')
    newf = open("messages.pot", 'r')
    
    while True:
        line = newf.readline()
        if not line:
            break
        if line.startswith('msgid'):
            idstr = line[5:].strip()
            f.write(line)
            if olddict.has_key(idstr): 
                f.write('msgstr %s\n' % (olddict[idstr]))
            else:
                f.write('msgstr ""\n')

            newf.readline()
        else:
            f.write(line)

    newf.close()
    f.close()
   
merge()


