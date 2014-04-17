from socket import *
from multiprocessing import Process
import sys
import time
import os
import shutil
import glob
import multiprocessing as mp

# CPSC 4910
# Spring 2014
# Team FitNet
# James Keeler, Daniel Joyner, Noah Falkie

# Description: This program is intended to read a video file, capture still
# from the frames of this video, store the image to the HDD, open a connection
# to the receiver(s), packetize the images, send the packets via UDP, delete
# the images once all packets have been sent, and close the connection(s).

# The image must be an HD video that is 1920x1080 with a playback frame rate
# of 30 fps.

# FFMPEG is required to be located in the same folder as this program, along
# with all of the requisite DLLs that FFMPEG needs. These are normally in its
# BIN folder.

# The receiver program must be launched prior to launching the sender.

# This program is multiprocessed. It spins up one process that captures still
# images from the video, and another process that sends these images to the 
# receiver(s).


# Captures still images from the FitNet video
# Currently, this is only capturing 5 seconds worth of images (150 images)
# All captured images will begin with "foo-"
# All captured images will be uncompressed bitmaps
def video2images():
    file="fire_ice1_1080.mp4" #Enter your file name
    os.system('ffmpeg -i '+file+' -vsync 0 -s hd1080 -r 30 -t 5 -f image2 foo-%05d.bmp 2> nul')


# Sends data packets to a target computer
# targetIP - the IP address or host name of the target computer
# dataToSend - the data packet to be sent
# socketToUse - the network socket to use when sending the data
def sendToHost(targetAddress, dataToSend, socketToUse):
    port = 42524                                    # A random port to be used for communication. MUST MATCH THE PORT OF THE RECEIVER.
    URI = (targetAddress,port)                      # Object containing the IP address or host name and port number
    socketToUse.sendto(dataToSend,URI)              # Send the data to the target machine


# Opens a connection to the receiver(s), sends the images, deletes the images, 
# closes the connection(s)
def send():
    UDPSocket = socket(AF_INET,SOCK_DGRAM)          # SOCK_DGRAM denotes the UDP protocol
    host = sys.argv[1]                              # The command line arguments are IP addresses of the receivers
    buf = 5760                                      # 1920 pixels x 3 color bytes per pixel = 5760 bytes per line

    # Counters
    timeList = []
    totalTime = 0.0
    frameCounter = 0

    frameCounter = 10000                            # Need to add leading zeros to fill up all 4 bytes

    while glob.glob("*.bmp"):                       # Returns a collection of all files with names matching this pattern
        file_name = str(glob.glob("*.bmp")[0])      # First name in the collection
        count = 0                                   # Packet counter
        lineCounter = 10000                         # Need to add leading zeros to fill up all 4 bytes
        timeBegin = time.time()                     # Time stamp
        f = open(file_name,'rb')                    # Open the image file. "rb" means read-only, binary file
        data = f.read(buf)                          # Read the first 5760 bytes (a full line of pixels)

        while (data):
            # This is a delay loop because time.sleep doesn't work for delays less 
            # than 1 millisecond.  2500 iterations takes about 0.25 ms. If there is 
            # more than 1 target computer, the act of sending the data provides 
            # enough delay
            if (len(sys.argv) == 2):
                for i in range(5000):
                    pass

            # Remove the leading 1 from the line number, leaving the line number and
            # leading zeros. Then encode that as UTF-8 and convert it to a bytes array.
            # Then prepend that array to the front of the image data.
            data = str(lineCounter)[1:].encode('utf-8') + data

            # Prepend the frame counter to the front of the data just like line number
            data = str(frameCounter)[1:].encode('utf-8') + data

            # sys.argv contains the command line arguments, each argument with 
            # an index greater than 1 should be an IP address or host name of 
            # a target computer
            for i in range(1, len(sys.argv)):       # Start at index 1, return a range from 1 to (number of command line arguments - 1)
                sendToHost(sys.argv[i], data, UDPSocket)    # Send the data packet to all target hosts
            
            # Read the next buffer-full of data
            data = f.read(buf)

            lineCounter += 1
            count += 1        

        f.close()                                   # Close the file
        timeEnd = time.time()                       # Time stamp
        print('Frame: {0:4d} complete. Sent {1:4d} packets in {2:>6.1f} ms.'.format(frameCounter - 10000, count, (timeEnd - timeBegin) * 1000))
        timeList.append((timeEnd - timeBegin) * 1000)   # Add duration to the collection (will be used to determine min and max durations)
        totalTime += ((timeEnd - timeBegin) * 1000)     # Will be used to calculate average duration
        frameCounter += 1
        os.system('del ' + file_name)               # Delete the image file

    UDPSocket.close()                               # Close the UDP socket
    timeList.sort()                                 # By sorting the list we can easily get the min and max values

    print(' ')
    print('Statistics for the transmission of {0} frames of video:'.format(frameCounter - 10000))
    print('    Packets sent : {0}'.format((frameCounter - 10000) * 1081))
    print(' ')
    print('    Max time     : {0:>6.1f} ms'.format(timeList[-1]))
    print('    Min time     : {0:>6.1f} ms'.format(timeList[0]))
    print('    Avg time     : {0:>6.1f} ms'.format(totalTime / (frameCounter - 10000)))

if __name__ == '__main__':
    if (len(sys.argv) > 1):
        v = Process(target=video2images, args=())       # Create a new process to run the video2images function
        s = Process(target=send, args=())               # Create another process to send images
        v.start()                                       # Start the first process
        time.sleep(1)                                   # Wait 1 second to allow the computer to be able to capture some images
        s.start()                                       # Begin sending those images
        v.join()                                        # Clean up the processes
        s.join()
