####################################################################################################
#  Enter a destination coordinate. The car will pivot turn to the destination coordinate and then  #
#   move forward towards the coordinate along with calculating the latency.                        #
#                                                                                                  #
#   Authors: Zarin Saifee & Stephanie Torres                                                       #
####################################################################################################

import socket   
import time
import math
import os
import sys
sys.path.insert(0, os.path.abspath('/home/raspberrypi/PiCarAutonomousDriving/example/Original_RaspberryPi_Code/SunFounder_Line_Follower'))
import Line_Follower
from picar import front_wheels
from picar import back_wheels
from datetime import datetime
import picar

#########################################################################################
#  Create a socket object and establish a connection to the remote server using the     #
#   server's IP address and port.                                                       #
#########################################################################################

# Initialize the socket for communication
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.200.207.132', 12345)  
#.132 (zarin IP)
sock.connect(server_address)    

# Initialize the last_coordinate variable
last_coordinate = None  

# Setup the picar
picar.setup()

# Define the forward and backward speeds
forward_speed = 50
backward_speed = 35

# Initialize the front and back wheels
fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
fw.ready()
bw.ready()

# Set the maximum turning angle
fw.turning_max = 45

#########################################################################################
#  Calculate the angle and distance between the current and new coordinates.            #
#                                                                                       #
#    Parameters:                                                                        #
#        - current_coordinate (tuple): The current coordinate.                          #
#        - new_coordinate (tuple): The new coordinate.                                  #
#                                                                                       #
#    Returns:                                                                           #
#        - angle (float): The calculated angle.                                         #
#        - distance (float): The calculated distance.                                   #
#########################################################################################

def calculate_distance(current_coordinate, new_coordinate):
    dx = new_coordinate[0] - current_coordinate[0]
    dy = new_coordinate[1] - current_coordinate[1]
    
    distance = math.sqrt(dx**2 + dy**2)
    return distance

#########################################################################################
#  Perform a pivot turn where the back wheels turn opposite of eachother to perform a   #
#   turn.                                                                               #
#########################################################################################
def pivot_turn():
    time.sleep(1.0)
    bw.speed = 45
    bw.left_wheel.backward()
    bw.right_wheel.forward()

#########################################################################################
# The move function calculates the travel time required for the robot to movea specific #
#   distance at a predefined speed. This helps determine the latency.                   #
#########################################################################################
def move(distance):
    global moveTime # Variable for Latency
    moveTime = datetime.now() # Record the current time 
    
    # Print the time for testing purposes
    print("The time by the movement is: ")
    print(moveTime)
    
    # Calculate the travel time
    travel_time = distance/forward_speed
    
    # Print travel time for testing purposes
    print("Travel time: ")
    print(travel_time)

    #Set speed of motors
    bw.speed = forward_speed
    bw.forward()
    
    # Pause the travel time
    time.sleep(travel_time)
    bw.speed = 0
    bw.stop()
    
#########################################################################################
#  The end function stops the Raspberrypi and turn the front wheels straight.           #
#########################################################################################
def end():
    bw.stop()
    fw.turn(90)

#########################################################################################
#  In the terminal this will ask the user to give an x and y coordinate.                #                                                 
#                                                                                       #
#    Returns:                                                                           #
#       - (x, y) (tuple): The user's coordinate.                                        #
#########################################################################################
def get_user_coordinate():
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)

#########################################################################################
# The main function to receive data, get user coordinate, calculate angle and distance, #
#   and move the car.                                                                   #
#                                                                                       #
#      - The code also calculates the Latency of how long the calculation takes.        #
#       - Useful for the start and stop testing in order to allow a smooth travel       #
#########################################################################################
def main():
    data = sock.recv(16)    # Recieve data from server reading 16 bytes of data
    if data:

        # Retrieve coordinate data from camera
        coordinate = data.decode('utf-8')   # Decode data from byte to string

        # Ask the user for a new coordinate
        new_coordinate = get_user_coordinate()

        print("The destination coordinate: ")
        print(new_coordinate)
        
        # Split the coordinate into x and y component (x,y)
        coordinate_split = coordinate.split(",")
        print(coordinate_split)
        x_coord_str = coordinate_split[0]
        y_coord_str = coordinate_split[1]

        # Turn x and y from a string to an integer
        x_coord = int(x_coord_str)
        y_coord = int(y_coord_str)

        # Create a Tuple (Store multiple items in a variable) 
        coordinate_int = (x_coord, y_coord)

        #Print current position for testing purposes
        print("Current Coordinate Int: ")
        print(coordinate_int)

       # To determine latency we use the datetime code to calculate how long the calculation takes
        now = datetime.now()
        print("The current time is : ")
        print(now)

        # Calculate angle and distance to the new coordinate
        distance = calculate_distance(coordinate_int, new_coordinate)
        print("The distance is: ")
        print(distance)

        # Move the robot to the new coordinate
        move(distance)

        # Calculate latency (How long calculation takes)
        latency = moveTime - now
        print("The latency is: ")
        print(latency)


if __name__ == '__main__':
    try:
         while True:
            main()
    except KeyboardInterrupt:
         end()  

# Close the socket
sock.close()