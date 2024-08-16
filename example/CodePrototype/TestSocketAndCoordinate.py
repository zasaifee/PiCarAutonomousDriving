#########################################################################################
#  The code refers to the testing of the socket with the code to determine if it is     #
#   functional, along with attempting to write code to determine the raspberryp         #
#   from one starting point to another.                                                 #
#                                                                                       #
#   Authors:  Zarin Saifee & Stephanie Torres                                           #
#########################################################################################

import socket  # Library of Low-level networking interfaces 
import time
import math
import os
import sys
sys.path.insert(0, os.path.abspath('/home/raspberrypi/PiCarAutonomousDriving/example/Original_RaspberryPi_Code/SunFounder_Line_Follower'))
import Line_Follower
from picar import front_wheels
from picar import back_wheels
import picar

#########################################################################################
# Create a socket object and establish a connection to the remote server using the      #
#  server's IP address and port.                                                        #
#########################################################################################

# Create socket object (IP address for IPv4, Indicate we are using TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server's address and port
server_address = ('10.200.204.10', 12345)  # Use laptop IP
sock.connect(server_address)    # Establish the connecton to remote server

last_coordinate = None  # Variable to store last recieved coordinate

# General PiCar setup
picar.setup()

forward_speed = 50
backward_speed = 35

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')

fw.ready()
bw.ready()
fw.turning_max = 45

home_coordinate = (52,135)

#########################################################################################
#  A function to calculate the angle and distance between the current coordinate and    #
#   new coordinate.                                                                     #
#########################################################################################

def calculate_angle_and_distance(current_coordinate, new_coordinate):
    
    # Calculate the difference of the new coordinate vs the old coordinates
    dx = new_coordinate[0] - current_coordinate[0]
    dy = new_coordinate[1] - current_coordinate[1]

    # Print for testing purposes
    print("dy" + str(dy))
    print("dx" + str(dx))

    # Calculate the distance of the two coordinate positions via pythagoren theorem
    distance = math.sqrt(dx**2 + dy**2)
    print("distance = " + str(distance))

    # Calculate the angle in radians based on python structure
    divVal = dy / dx
    angle_rad = math.atan(divVal)
    print("angle_rad = " + str(angle_rad))

    # Convert to degrees to determine and test if angle is correct
    angle = math.degrees(angle_rad)
    print("degree = " + str(angle))

    # Possible test to give it a boundry to accomodate for negative or max coordinates
        # if angle < 0: 
        #     angle  = 360 + angle
        #angle = 90 - angle
    
    # Print for test purposes
    print("angle = " + str(angle))

    # Create a bound due to raspberrypy only turning 45 deg left and right max
    angle = max(55, min(135, angle))
    print("Angle bound = " + str(angle))

    return angle, distance

#########################################################################################
#  A function to move the Raspberrypi based on the angle and distance calculated.       #
#########################################################################################

def move(angle, distance):

    # Calculate the travel time based off distance and speed
    travel_time = distance/forward_speed
    print("turning" + str(angle))
    fw.turn(angle)

    # Sets backwheels forward speed
    bw.speed = forward_speed
    time.sleep(5.0)     
    bw.forward()

    # Allows the car forward based on travel time
    time.sleep(travel_time)
    print("Stopping car")

    bw.stop()
    time.sleep(5.0)  ## Added time for sleep in order have longer wait
                     ## or else it would stop and go right away 

#########################################################################################
#  The end funciton stops the Raspberrypi and set reset the wheels back to 90 degrees   #
#########################################################################################

def end():
    bw.stop()
    fw.turn(90)

#########################################################################################
#  The function will get the users input on the new coordinate to go to.                #
#########################################################################################

def get_user_coordinate():
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)

current_coordinate = home_coordinate

#########################################################################################
#  This section of the code recieves the data from the server and move based on the     #
#   recieved coordinates.                                                               #
#########################################################################################

while True:
    data = sock.recv(16)    # Recieve data from server reading 16 bytes of data
    if data:    # If data recieved
        coordinate = data.decode('utf-8')

        print('Current coordinate: {!r}'.format(coordinate))
     # Ask the user for a new coordinate
        new_coordinate = get_user_coordinate()
        print(new_coordinate)

        print("Current Coord: ")    
        print(current_coordinate)
        
        # Calculate angle and distance to the new coordinate
        angle, distance = calculate_angle_and_distance(current_coordinate, new_coordinate)
        
         # Move the robot to the new coordinate
        move(angle, distance)

    else:
        break

#After all is done
sock.close()