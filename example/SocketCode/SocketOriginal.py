######################################################################################################################
# This code is the original socket code that was first used to test if the socket is working in general. This fall   #
#   into line with recieving the camera coordinates that pulls from the txt  file.                                   #
#                                                                                                                    #    
#  How it works:                                                                                                     #
#    - This code works with a seprate laptop which uses the IP and run it through the VS Code remote explorer        #
#        in order to connect to the Raspberrypi to communicate the data.                                             #
#    - Doing so is important so that the Raspberrypi is not running so much content and code at the same time.       #
#                                                                                                                    #
#  Author:  Stephanie Torres                                                                                         #
#                                                                                                                    #
#  Resources:                                                                                                        #
#      - https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python?irclickid=x1aTS8x1jxyKR43WKz34lXhqUkHQpuXW0UJx1Y0&irgwc=1&utm_medium=affiliate&utm_source=impact&utm_campaign=000000_1-2003851_2-mix_3-all_4-na_5-na_6-na_7-mp_8-affl-ip_9-na_10-bau_11-Bing%20Rebates%20by%20Microsoft&utm_content=BANNER&utm_term=EdgeBingFlow
#      - https://www.pythoncentral.io/guide-to-socket-programming-in-python-easy-examples/                           #
#      - https://www.geeksforgeeks.org/socket-programming-python/                                                    #
#                                                                                                                    #
######################################################################################################################

import socket   # Library of Low-level networking interfaces 
import time
import math
import os
import sys
sys.path.insert(0, os.path.abspath('/home/raspberrypi/PiCarAutonomousDriving/example/Original_RaspberryPi_Code/SunFounder_Line_Follower'))
import Line_Follower
from picar import front_wheels
from picar import back_wheels
import picar

# Create socket object (IP address for IPv4, Indicate we are using TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server's address and port
server_address = ('10.200.207.224', 12345)  # Use laptop IP
sock.connect(server_address)    # Establish the connecton to remote server

last_coordinate = None  # Variable to store last recieved coordinate

# Start of data transfer 
# Receive the data in small chunks and perform your actions
while True:
    data = sock.recv(16)    # Recieve data from server reading 16 bytes of data
    if data:    # If data recieved
        coordinate = data.decode('utf-8')   # Decode data from byte to string
        print('received {!r}'.format(coordinate))   # r! convert value to string
        # Check if the coordinate has changed
        if coordinate != last_coordinate:
            print('Coordinate change detected!')
            last_coordinate = coordinate
    else:
        break

#After all is done
sock.close()