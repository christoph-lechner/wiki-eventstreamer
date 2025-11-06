#!/usr/bin/env python3

import datetime
import time

class FilenameGen:
    def __init__(self):
        self.tnow = datetime.datetime.now()
        self.tprev = self.tnow

        self.min_switch = 35 # minute of the hour when to switch to next file
        self.datadir = 'streamdata' # data dir without trailing slash
        self.seq = 1

    def qq(self):
        self.tprev = self.tnow
        self.tnow = datetime.datetime.now()
        do_switch = self.tprev.minute<self.min_switch and self.tnow.minute>=self.min_switch
        return do_switch

    def getfn(self):
        s = self.datadir+'/stream_' + self.tnow.strftime('%Y%m%dT%H%M%S') + '_' + f'{self.seq:09d}'
        self.seq+=1
        return(s)


"""
fng = FilenameGen()
fout = open(fng.getfn(),'w')
while True:
    if fng.qq():
        print('newfile')
        fout.close()
        fout = open(fng.getfn(),'w')
    time.sleep(1)
"""
