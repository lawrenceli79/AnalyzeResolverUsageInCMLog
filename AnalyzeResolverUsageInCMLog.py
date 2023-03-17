"""\
This script is to analyze Resolver usage in all DRSCM_{Date}.log files in given {folder}
Usage: {folder}
"""

import sys
import re
import os

if (len(sys.argv)<=1):
    print ("Usage: py {} <Folder> ".format(__file__))
    sys.exit()

strInFolder = sys.argv[1]

# Output resolver usage in a single row
def Output(dirpath:str, fname:str, resolvers:[], resolverPick:str, timestr:str):
    if(len(resolvers)==0):
        return
    strOut = ""
    strOut += dirpath + ","
    strOut += fname + ","
    strOut += timestr + ","
    if(resolverPick!=""):
        i = resolvers.index(resolverPick)
        strOut += "{},{},".format(i, resolverPick)
    else:
        strOut += "NA,NA,"
    strOut += ",".join(resolvers)
    print(strOut)

# Analyze a given log file
def AnalyzeFile(dirpath:str, fname:str):
    fullpath = dirpath +"/" + fname
    with open(fullpath, mode="r", errors='ignore') as fInFile:
        timestr = ""
        resolvers = []
        for i,line in enumerate(fInFile):
            if(mo := re.search("^(\d+ \d+ ).*N\.AddResolver: OK, ([0-9a-f:]+)", line)):
                timestr = mo.group(1)
                resolver = mo.group(2)
                resolvers.append(resolver)
            elif(mo := re.search("N\.DoResolve: BeginResolveFromResolver OK, ([0-9a-f:]+)", line)):
                resolver = mo.group(1)
                Output(dirpath, fname, resolvers, resolver, timestr)
                #resolvers.clear()
            elif(re.search("N\.ClearResolver: OK", line)):
                #Output(dirpath, fname, resolvers, "")
                resolvers.clear()
            elif(re.search("N\.CNode\(\)", line)):
                resolvers.clear()


strHeader = "Folder,File,Time,iRPck,RPck"
for i in range(0, 7):
    strHeader += ",Resolver{}".format(i)
print(strHeader)

for dirpath, dnames, fnames in os.walk(strInFolder + "/"):
    for fname in fnames:
        AnalyzeFile(dirpath, fname)
