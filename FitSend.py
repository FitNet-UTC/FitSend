from socket import *
import sys
import time

timeBegin = time.time()

s = socket(AF_INET,SOCK_DGRAM)
host =sys.argv[1]
port = 42524
buf = 8192
addr = (host,port)

file_name=sys.argv[2]

f=open(file_name,'rb') 
data = f.read(buf)

#s.sendto(file_name,addr)
s.sendto(data,addr)
count = 0
while (data):
    count += 1
    if(s.sendto(data,addr)):
        data = f.read(buf)

timeEnd = time.time()
print('Transmission complete. Sent ' + str(count) + ' packets in ' + str(timeEnd - timeBegin) + ' seconds.')
s.close()
f.close()
