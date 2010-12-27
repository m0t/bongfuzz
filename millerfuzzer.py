#!/usr/bin/python

#temporary call format ./millerfuzzer.py inputfile outputfile

import random,math,array
import os,sys

ifile = open(sys.argv[1])
ofile = open(sys.argv[2], 'w')
FuzzFactor = 10

strbuf=ifile.read()

if len(strbuf) == 0:
  	print "empty inputfile"
   	sys.exit(-1)
buf = array.array('c')
buf.fromstring(strbuf)
numwrites=random.randrange(math.ceil(float( (len(buf))/FuzzFactor)))+1
for j in xrange(numwrites):
  	rbyte=random.randrange(256)
   	rn=random.randrange(len(buf))
   	buf[rn] = "%c"%(rbyte)
#print  buf.tostring()
strbuf = buf.tostring()

ofile.write(strbuf)
ofile.close()
