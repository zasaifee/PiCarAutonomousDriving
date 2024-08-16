#########################################################################################
# Enter a destination coordinate. The car will pivot turn to the destination coordinate #
#   and then move forward towards the coordinate.                                       #
#                                                                                       #
#   Authors: Zarin Saifee & Stephanie Torres                                            #
#########################################################################################

import socket   
import time
import math
import os
import sys
sys.path.insert(0, os.path.abspath('/home/raspberrypi/PiCarAutonomousDriving/example/Original_RaspberryPi_Code/SunFounder_Line_Follower'))
import Line_Follower
from picar import front_wheels
from picar import back_wheels
import picar
import ast

#########################################################################################
#  Create a socket object and establish a connection to the remote server using the     #
#   server's IP address and port.                                                       #
#########################################################################################

# Initialize the socket for communication
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.200.207.132', 12345)  
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

# Define the home coordinate
home_coordinate = (-151,139)

#########################################################################################
#  Calculate the angle and distance between the current and new coordinates.            #
#                                                                                       #
#    Parameters:                                                                        #
#       - current_coordinate (tuple): The current coordinate.                           #
#       - new_coordinate (tuple): The new coordinate.                                   #
#                                                                                       #
#    Returns:                                                                           #
#       - angle (float): The calculated angle.                                          #
#       - distance (float): The calculated distance.                                    #
#########################################################################################

def calculate_angle_and_distance(current_coordinate, new_coordinate):
    dx = new_coordinate[0] - current_coordinate[0]
    dy = new_coordinate[1] - current_coordinate[1]
    
    distance = math.sqrt(dx**2 + dy**2)
    angle_rad = math.atan2(dy, dx)
    angle = math.degrees(angle_rad)
    return angle, distance


#########################################################################################
# This funciton will make the backwheels turn opposite of eachother in other to perform #
#   a pivot turn.                                                                       #
#########################################################################################

def pivot_turn():
    time.sleep(1.0)
    bw.speed = 45
    bw.left_wheel.backward()
    bw.right_wheel.forward()


#########################################################################################
#  The function will move the Raspberrypi car based on the given angle and distance.    #
#                                                                                       #
#    Parameters:                                                                        #
#       - angle (float): The angle to turn.                                             #
#       - distance (float): The distance to move.                                       #
#########################################################################################

def move(angle, distance):
    travel_time = distance/forward_speed
    print("Travel time: " + str(travel_time))

    turn_ratio = 1/18
    turning_time = (abs(angle)*turn_ratio) 
    print("Turning Time: " + str(turning_time))

    pivot_turn()
    time.sleep(turning_time)
    bw.speed = 0
    bw.stop()

    time.sleep(2.0)

    fw.turn_straight()
    bw.speed = forward_speed
    bw.forward()
    time.sleep(travel_time)
    bw.stop()

    time.sleep(5.0)


#########################################################################################
#  The end function will stop the Raspberrypi car and turn the front wheels straight.   #
#########################################################################################

def end():
    bw.stop()
    fw.turn(90)


#########################################################################################
#  The function will ask the user in the terminal for a new coordinate input.           #
#                                                                                       #
#  Returns:                                                                             #
#     - (x,y) (tuple): The user's coordinate                                            #
#########################################################################################

def get_user_coordinate():
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)

# Define the current coordinate
current_coordinate = home_coordinate


##########################################################################################
#  The main function to receive data, get user coordinate, calculate angle and distance, #
#    and move the car.                                                                   #
##########################################################################################
def main():
    data = sock.recv(16)    # Recieve data from server reading 16 bytes of data
    if data:
        coordinate = data.decode('utf-8')   # Decode data from byte to string

        # Split the coordinate into x and y component (x,y)
        coordinate_split = coordinate.split(",") 
        x_coord_str = coordinate_split[0]
        y_coord_str = coordinate_split[1]

        # Turn x and y from a string to an integer
        x_coord = int(x_coord_str)
        y_coord = int(y_coord_str)

        # Create a Tuple (Store multiple items in a variable) 
        coordinate_int = (x_coord, y_coord)
        
        # Print current position
        print("Current Coordinate Int: ")
        print(coordinate_int)

        # Ask the user for a new coordinate
        new_coordinate = get_user_coordinate()
        print(new_coordinate)

        print("Current Coord: ")    
        print(current_coordinate)
            
        # Calculate angle and distance to the new coordinate
        angle, distance = calculate_angle_and_distance(coordinate_int, new_coordinate)
            
        # Move the robot to the new coordinate
        move(angle, distance)

        # Print for test purposes
        print(angle)
        print(distance)


if __name__ == '__main__':
    try:
         while True:
             main()
    except KeyboardInterrupt:
         end()  

# Close the socket
sock.close()