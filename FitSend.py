from socket import *
import sys
import time

timeBegin = time.time()

s = socket(AF_INET,SOCK_DGRAM)
host =sys.argv[1]
port = 42524
buf = 5760
addr = (host,port)

file_name=sys.argv[2]

# Packet counter
count = 0

# Need to add leading zeros to fill up all 4 bytes
lineCounter = 10000

f=open(file_name,'rb') 
data = f.read(buf)

while (data):
    count += 1    
    # Remove the leading 1 from the line number, leaving the line number and 
    # leading zeros. Then encode that as UTF-8 and convert it to a bytes array.
    # Then prepend that array to the front of the image data.
    data = str(lineCounter)[1:].encode('utf-8') + data
    if(s.sendto(data,addr)):
        data = f.read(buf)
        lineCounter += 1

timeEnd = time.time()
print('Transmission complete. Sent ' + str(count) + ' packets in ' + str(timeEnd - timeBegin) + ' seconds.')
s.close()
f.close()
