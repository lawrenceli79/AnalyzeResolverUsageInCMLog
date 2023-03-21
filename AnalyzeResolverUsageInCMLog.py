"""\
This script is to analyze Resolver usage in all DRSCM_{Date}.log files in given {folder}
Usage: {folder}
"""

import sys
import re
import os
from dataclasses import dataclass

@dataclass
class Resolver:
    ipv6: str
    domain: str
    port: int
def FindResolverByIp(resolvers:[Resolver], ip:str, port:int) -> int: 
    ipick = -1
    n = len(resolvers)
    for i in range(len(resolvers)):
        r = resolvers[i]
        if(r.ipv6 == ip and r.port == port):
            ipick = i
            break
    return ipick
def FindResolverByDns(resolvers:[Resolver], domain:str, port:int) -> int: 
    ipick = -1
    n = len(resolvers)
    for i in range(len(resolvers)):
        r = resolvers[i]
        if(r.domain == domain and r.port == port):
            ipick = i
            break
    return ipick


# Output resolver usage in a single row
def Output(dirpath:str, fname:str, timestr:str, req:str, resolvers:[Resolver], i:int, bIsIpv6:bool) -> None:
    if(len(resolvers)==0):
        return
    strOut = ""
    strOut += dirpath + ","
    strOut += fname + ","
    strOut += timestr + ","
    strOut += req + ","
    if(i>-1):
        addr = resolvers[i].ipv6 if bIsIpv6 else resolvers[i].domain
        ipv = "ipv6" if bIsIpv6 else "ipv4"
        strOut += "{},{}[{}],{}".format(i, addr, resolvers[i].port, ipv)
    else:
        strOut += "NA,NA,NA"
    for r in resolvers:
        strOut += ",{}[{}]".format(r.ipv6, r.port)
    print(strOut)

# Analyze a given log file
def AnalyzeFile(dirpath:str, fname:str):
    fullpath = dirpath +"/" + fname
    with open(fullpath, mode="r", errors='ignore') as fInFile:
        timestr = ""
        resolvers = []
        for i,line in enumerate(fInFile):
            if(mo := re.search("^(\d+ \d+ ).*N\.AddResolver: OK, ([0-9a-f:]+) ([\w.]+)  \[(\d+)\]", line)):
                timestr = mo.group(1)
                ipv6 = mo.group(2)
                domain = mo.group(3)
                port = (int)(mo.group(4))
                r = Resolver(ipv6, domain, port)
                resolvers.append(r)
            #elif(mo := re.search("N\.DoResolve: BeginResolveFromResolver OK, ([0-9a-f:]+)\[(\d+)\]", line)):
            elif(mo := re.search("RS\.(\w+): SendRequest\(([0-9a-f:]+), (\d+),", line)):
                req = mo.group(1) 
                addr = mo.group(2)
                port = (int)(mo.group(3))
                iResolver = FindResolverByIp(resolvers, addr, port)
                Output(dirpath, fname, timestr, req, resolvers, iResolver, True)
            #elif(mo := re.search("N\.DoResolve: BeginResolveFromResolver OK, ([\w.]+)\[(\d+)\]", line)):
            elif(mo := re.search("RS\.(\w+): SendRequest\(([\w.]+), (\d+),", line)):
                req = mo.group(1) 
                addr = mo.group(2)
                port = (int)(mo.group(3))
                iResolver = FindResolverByDns(resolvers, addr, port)
                Output(dirpath, fname, timestr, req, resolvers, iResolver, False)
            elif(re.search("N\.ClearResolver: OK", line)):
                resolvers.clear()
            elif(re.search("N\.CNode\(\)", line)):
                resolvers.clear()



if (len(sys.argv)<=1):
    print ("Usage: py {} <Folder> ".format(__file__))
    sys.exit()
strInFolder = sys.argv[1]

strHeader = "Folder,File,Time,Request,iRPck,RPck,ipv4/6"
for i in range(0, 7):
    strHeader += ",Resolver{}".format(i)
print(strHeader)

for dirpath, dnames, fnames in os.walk(strInFolder + "/"):
    for fname in fnames:
        AnalyzeFile(dirpath, fname)
