#################################################################################################
# This script controls a robot car using socket communication to receive coordinate data.       #
#   It connects to a server at a specified IP address and port, receives coordinate updates,    #
#   and moves the car toward the target coordinate until it reaches within a certain distance.  #
#                                                                                               #
#   Author: Stephanie Torres and Zarin Saifee                                                   #
#                                                                                               #
#   Usage:                                                                                      #
#       1. Make sure the server is running and providing coordinate data.                       #
#       2. Adjust the server address and port in the 'server_address' variable.                 #
#       3. Run this script to control the robot car.                                            #
#                                                                                               #
#   Dependencies:                                                                               #
#       - picar library (install using 'pip install picar')                                     #
#                                                                                               #
#   Note: Replace the placeholder IP addresses with the actual server IP addresses.             #
#                                                                                               #
#################################################################################################
 
import socket   
import time
import math
from picar import front_wheels
from picar import back_wheels
from datetime import datetime
import picar
import re
import Gryo_Multiprocessing as gyro

#########################################################################################
#  Create a socket object and establish a connection to the remote server using the     #
#   server's IP address and port.                                                       #
#########################################################################################

# Initialize the socket for communication
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.200.204.87', 12345)
sock.connect(server_address)    

# Initialize the last_coordinate variable
last_coordinate = None  

# Setup the picar
picar.setup()

# Initialize robot car parameters
forward_speed = 50
backward_speed = 35

# Initialize the front and back wheels
fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
fw.ready()
bw.ready()

# Set the maximum turning angle
fw.turning_max = 45

#######################################################################################
#  Calculate the angle and distance between the current and new coordinates. For the  #
#   purposes of testing and understanding the code we focused on the y direction in   #
#   order to make the calculations understandable 
#                                                                                     #
#    Parameters:                                                                      #
#       - current_coordinate (tuple): The current coordinate.                         #
#       - new_coordinate (tuple): The new coordinate.                                 #
#                                                                                     #
#    Returns:                                                                         #
#       - float: Difference between y-coordinates.                                    #
#######################################################################################

def calculate_distance(current_coordinate, new_coordinate):
    dy = current_coordinate[1] - new_coordinate[1]
    return dy


#################################################################################
# Moves the Raspberrypi car from coordA to coordB.                              # 
#                                                                               #
#    Args:                                                                      #
#        coordA (tuple): Starting (x, y) coordinate.                            # 
#        coordB (tuple): Target (x, y) coordinate.                              #
#################################################################################

def move(coordA, coordB):
    if coordA == coordB:
        end()
        return
    else:
        bw.speed = forward_speed
        bw.forward()
        time.sleep(0.25) 
        bw.speed = 0
        bw.stop()
    

#################################################################################
#   Stops the robot car and turns the front wheels to 90 degrees.               #         
#################################################################################

def end():
    bw.stop()
    fw.turn(90)

#################################################################################
#  Gets user input for a new coordinate.                                        #
#                                                                               #
#   Returns:                                                                    #
#      - tuple: User-specified (x, y) coordinate.                               #
#################################################################################

def get_user_coordinate():
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)

#################################################################################
#  Main function to control the robot car based on received coordinate data.
#################################################################################

def main(): 
    # Get destination from the user and print for testing
    new_coordinate = get_user_coordinate()
    print("The destination coordinate: ")
    print(new_coordinate)

    # Initialize three variables 
    prev_distance = 0
    distance = 0
    coordinate_int = (0,0)
    
    while True:
        # Recieve the bytes of coordinate data from the socket
        data = sock.recv(1024) 

        # If the data is recieved   
        if data:
            # Decode the data from byte to string
            data_str = data.decode('utf-8')   
            
            # Every new x and y return for new line
            lines = re.split('\n|-', data_str)

            # Iterate over each line
            for line in lines:
                if not line:
                    continue
                
                # Formate the data into coordinate like strings x,y
                components = line.split(',')

                # There was a lot of error when recieving the socket data which made
                #  it difficult to get the proper data so the following is allowing a
                #  boundary which only pulls for the x and y coordinate and uses the
                #  proper data for the calculation.
                if len(components) == 2:
                    x_str, y_str = components
                    
                    # If both components are not empty
                    if x_str and y_str:
                        # Convert the x and y to an integer
                        x_coord = int(x_str)
                        y_coord = int(y_str)
                        
                        # Create tuple with the coordinates
                        coordinate_int = (x_coord, y_coord)
                        print("Current Coordinate Int: ")
                        print(coordinate_int)
                else:
                    continue

                # Calculate the distance from current to new destination
                distance = calculate_distance(coordinate_int, new_coordinate)
                print("The current distance: ")
                print(distance)

                # Due the coordinates and robot not being able to reach the exact
                #  new coordinate we gave it a bound to end if it reached if the 
                #  new distance is around less than 10 of the new y coordinate.
                if distance <= 10:
                    end()
                    return
                
                time.sleep(1.0)

                # Move towards the destination
                move(coordinate_int, new_coordinate)

                # Update the distance as the previous distance and print for testing
                prev_distance = distance
                print(prev_distance)

if __name__ == '__main__':
    try:
         while True:
            main()
    except KeyboardInterrupt:
         end()  
    finally:
        sock.close()