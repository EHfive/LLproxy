#!/usr/bin/python3
import sys
import subprocess as sp

try:
    texbpath = sys.argv[1]
except IndexError:
    texbpath = input()

imginfo = sp.Popen(['texb', '-a', texbpath], stdout=sp.PIPE, stderr=sp.STDOUT)
info = {}
for line in imginfo.stdout:
    line = line.decode()
    try:
        line.index('    ')
        b = line.index(':')
    except ValueError:
        continue
    else:
        img_name = line[4:b]
        info[img_name.split('/')[-1]] = img_name
png_path = ' '
while png_path[0] not in ['e', 'exit', 'q', 'quit']:
    png_path = input("png file path:").strip('"\'\t ').split(' ')
    for png in png_path:
        try:
            png = png.strip('"\'\t ')
            img_name = info[png.split('/')[-1].split('.png')[0]]
            sp.call(['texb', '-r', img_name + ':' + png, texbpath])
        except KeyError:
            print('未匹配到', png.strip(' \t"\'').split('/')[-1].split('.png')[0])
sp.call(['texb', '-t', texbpath])
