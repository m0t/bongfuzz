#!/usr/bin/python

#similar to hongfuzz, without instrumentation, set windbg as jit debugger
#launch process iterating multiple times on each test case, 
#fuzzing each time with a random component, fuzzing must support load of external fuzzer

#NOTE: since bongfuzz is written with fuzzing firefox in mind, fuzzing happens one 
#istance at the time

#TODO:
#add pydbg to register unhandled exception

#so:
#load test case path list
#load fuzzer
#for each file
#    repeat n times:
#         fuzz inputfile to outputfile
#         call prog on fuzzed input


import subprocess 
import threading
import getopt
import time
import platform,os,sys
#import pedrpc

from pydbg		 import *
from pydbg.defines import *

import crash_binning 


ERR    = lambda msg: sys.stderr.write("ERR> " + msg + "\n") or sys.exit(1)
USAGE = "USAGE:./bongfuzz.py [<options>]"    \
        "\n\t-d           prints lots of debug msgs"    \
        "\n\t-t <time>    sets time interval between requests"    \
        "\n\t-s           restart fuzzing from session file \"fuzz_session.save\""    \
        "\n\t-S <file>    restart fuzzing from <file>"

url_list = "listfile.txt"
#XXX: do better than this
crash_bin = "C:\\crashdump.test"
#XXX: file:/// is needed only for firefox, need a way to set prefix when opening test_case
exe_path='C:\\program files\\mozilla firefox\\firefox.exe -new-window file:///'
restoreFlag = False
debugFlag = False
iterations=1000
sessionfile="fuzz_session.save"
timeInterval = 5

#fuzzing parameters
if platform.platform().find("Linux") >= 0:
    fuzzer="./millerfuzzer.py"
elif platform.platform().find("Window") >= 0:
    fuzzer="python millerfuzzer.py"
fuzzeropts=""
outputfile="temp.html"

def DEBUG(msg):
    global debugFlag
    if (debugFlag):
        sys.stderr.write("DEBUG: "+ msg +"\n")

#read input file, call fuzzer, return output file
def fuzz(inputfile):
    global fuzzer
    global fuzzeropts
    global outputfile
    DEBUG("fuzzer call: %s" % " ".join((fuzzer, fuzzeropts, inputfile)) )
    subprocess.Popen(" ".join((fuzzer, fuzzeropts, inputfile, outputfile)))
    return "\"%s\"" % os.getcwd()+"/"+outputfile

if __name__ == "__main__":
    # parse command line options.
    #if len(sys.argv) <= 1:
    #    ERR(USAGE)
    try:
        optlist,args = getopt.getopt(sys.argv[1:], 't:dhsS:')
    except getopt.GetoptError:
        ERR(USAGE)

    for o,a in optlist:
        if o == "-t":
            timeInterval = int(a)
        if o == "-s":
            restoreFlag = True
        if o == "-S":
            restoreFlag = True
            sessionfile = a
        if o == "-d":
            debugFlag = True
        if o == "-h":
            ERR(USAGE)    
    
    log_level = 1

    f=open(url_list)
    lines=f.readlines()

    if restoreFlag:
        #read sessionfile, extract linestart and iterstart
        sess = open(sessionfile, 'r+')
        linestart,itstart = sess.readline().split(",")
        linestart = int(linestart)
        itstart = int(itstart)
        print linestart,itstart
    else:
        linestart = 0
        itstart = 0
        sess = None
        
    try:        
        for l in range(linestart, len(lines)):
            testcase = str(lines[l].strip())
            print "/testcase: %s" % testcase
            currline=l
            #complete last interrupted iterations and then reset state
            for i in range(itstart,iterations):
                currit = i
                test_number =  currline*iterations+currit
                fuzzedcase=fuzz(testcase)
                #fuzz file and start process with test case
                DEBUG("test_number %d, iteration %d, testcase fuzzed, creating process: %s\n" % (test_number, currit, exe_path))
                #DEBUG(exe_path+fuzzedcase)
                inst = subprocess.Popen(exe_path + fuzzedcase) 
                time.sleep(timeInterval)
                inst.kill()
            
    except KeyboardInterrupt:
        #save file line and iter. count
        print "saving to sessfile "+sessionfile
        if not sess:
            sess = open(sessionfile, 'w')
        sess.seek(0)
        sess.write(str(currline)+","+str(currit))
        sess.truncate()
        sess.close
        sys.exit()
