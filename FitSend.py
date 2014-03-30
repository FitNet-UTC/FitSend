from socket import *
from multiprocessing import Process
import sys
import time
import os
import shutil
import glob
import multiprocessing as mp

def video2images():
    file="fire_ice1_1080.mp4" #Enter your file name
    os.system('ffmpeg -i '+file+' -vsync 0 -s hd1080 -r 30 -t 5 -f image2 foo-%05d.bmp 2> nul')

def send():
    s = socket(AF_INET,SOCK_DGRAM)
    host = sys.argv[1]
    port = 42524
    # 1920 pixels x 3 color bytes per pixel = 5760 bytes per line
    buf = 5760
    addr = (host,port)

    # Counters
    timeList = []
    totalTime = 0.0
    frameCounter = 0

    # Need to add leading zeros to fill up all 4 bytes
    frameCounter = 10000

    while glob.glob("*.bmp"):

        file_name = str(glob.glob("*.bmp")[0])

        # Packet counter
        count = 0

        # Need to add leading zeros to fill up all 4 bytes
        lineCounter = 10000

        timeBegin = time.time()

        f = open(file_name,'rb')
        data = f.read(buf)

        while (data):
            # This is a delay loop because time.sleep doesn't work for delays less than
            # 1 millisecond.  2500 iterations takes about 0.25 ms.
            for i in range(6500):
                pass

            # Remove the leading 1 from the line number, leaving the line number and
            # leading zeros. Then encode that as UTF-8 and convert it to a bytes array.
            # Then prepend that array to the front of the image data.
            data = str(lineCounter)[1:].encode('utf-8') + data

            # Prepend the frame counter to the front of the data just like line number
            data = str(frameCounter)[1:].encode('utf-8') + data

            # Send the data packet
            s.sendto(data,addr)
            
            # Read the next buffer-full of data
            data = f.read(buf)

            lineCounter += 1
            count += 1        

        f.close()
        timeEnd = time.time()
        print('Frame: {0:4d} complete. Sent {1:4d} packets in {2:>6.1f} ms.'.format(frameCounter - 10000, count, (timeEnd - timeBegin) * 1000))
        timeList.append((timeEnd - timeBegin) * 1000)
        totalTime += ((timeEnd - timeBegin) * 1000)
        frameCounter += 1
        os.system('del ' + file_name)

    s.close()

    # By sorting the list we can easily get the min and max values
    timeList.sort()

    print(' ')
    print('Statistics for the transmission of {0} frames of video:'.format(frameCounter - 10000))
    print('    Packets sent : {0}'.format((frameCounter - 10000) * 1081))
    print(' ')
    print('    Max time     : {0:>6.1f} ms'.format(timeList[-1]))
    print('    Min time     : {0:>6.1f} ms'.format(timeList[0]))
    print('    Avg time     : {0:>6.1f} ms'.format(totalTime / (frameCounter - 10000)))

if __name__ == '__main__':
    v = Process(target=video2images, args=())
    s = Process(target=send, args=())
    v.start()
    time.sleep(1)
    s.start()
    v.join()
    s.join()
