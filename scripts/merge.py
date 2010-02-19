# coding: utf-8
import os, sys

def merge(samplefile, fromfile, tofile):
    olddict = {}
    oldf = open(samplefile, 'r')
    while True:
        line = oldf.readline()
        if not line:
            break
        if line.startswith('msgid'):
            idstr = line[5:].strip()
            line2 = oldf.readline()
            vastr = line2[6:].strip()
            olddict[idstr] = vastr
        elif line.startswith('"Last-Translator'):
            olddict['"Last-Translator'] = line
            
    oldf.close()

    f = open(tofile, 'w')
    newf = open(fromfile, 'r')
    
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
        elif line.startswith('"Last-Translator'):
            f.write(olddict['"Last-Translator'])
        elif line.startswith('"'):
            line = line.replace('CHARSET', 'utf-8')
            line = line.replace('ENCODING', '8bit')
            f.write(line)
        else:
            f.write(line)

    newf.close()
    f.close()
 

def create_en(fromfile, tofile):
    fromf = open(fromfile, 'r')
    tof   = open(tofile, 'w')

    while True:
        line = fromf.readline()
        if not line:
            break

        if line.startswith('msgid'):
            idstr = line[5:].strip()
            tof.write(line)
            tof.write('msgstr %s\n' % (idstr))

            fromf.readline()
        elif line.startswith('"'):
            line = line.replace('CHARSET', 'utf-8')
            line = line.replace('ENCODING', '8bit')
            tof.write(line)
        else:
            tof.write(line)

    tof.close()
    fromf.close()


if __name__ == '__main__':
    #merge()
    pass


