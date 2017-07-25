#!/usr/bin/python3
import sys
import subprocess as sp
import requests as rq
import os
itsudemo_cmd='texb'
try:
    texbpath = sys.argv[1]
except IndexError:
    texbpath = input()
server_path = "https://r.llsif.win/"
imginfo = sp.Popen([itsudemo_cmd, '-a', texbpath], stdout=sp.PIPE, stderr=sp.STDOUT)
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

for short_name, img_name in info.items():

    png = '/home/cimoc/PycharmProjects/LLproxy/data/title/' + short_name + '.png'
    if not os.path.exists(png):
        req = rq.get(server_path + img_name + '.png')
        open(png, 'wb').write(req.content)
    sp.call([itsudemo_cmd, '-r', img_name + ':' + png, texbpath])
    print(short_name)
sp.call([itsudemo_cmd, '-t', texbpath])
