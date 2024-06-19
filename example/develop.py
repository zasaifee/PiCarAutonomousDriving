"""
Enter a destination coordinate. The car will pivot turn to the destination coordinate and then 
move forward towards the coordinate.

Authors: Zarin Saifee & Stephanie Torres
"""
import socket   
import time
import math
from SunFounder_Line_Follower import Line_Follower
from picar import front_wheels
from picar import back_wheels
from datetime import datetime
import picar
import re

# Initialize the socket for communication
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.200.204.10', 12345)  
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

# Define the home coordinate
#home_coordinate = (-151,139)

def calculate_distance(current_coordinate, new_coordinate):
    """
    Calculate the angle and distance between the current and new coordinates.

    Parameters:
    current_coordinate (tuple): The current coordinate.
    new_coordinate (tuple): The new coordinate.

    Returns:
    angle (float): The calculated angle.
    distance (float): The calculated distance.
    """
    dx = new_coordinate[0] - current_coordinate[0]
    dy = new_coordinate[1] - current_coordinate[1]
    
    distance = math.sqrt(dx**2 + dy**2)
    return distance

def pivot_turn():
    """
    Perform a pivot turn.
    """
    time.sleep(1.0)
    bw.speed = 45
    bw.left_wheel.backward()
    bw.right_wheel.forward()

def move(distance):
    global moveTime
    moveTime = datetime.now()
    print("The time by the movement is: ")
    print(moveTime)
    travel_time = distance/forward_speed
    print("Travel time: ")
    print(travel_time)
    bw.speed = forward_speed
    bw.forward()
    time.sleep(travel_time)
    bw.speed = 0
    bw.stop()    

def end():
    """
    Stop the car and turn the front wheels straight.
    """
    bw.stop()
    fw.turn(90)

def get_user_coordinate():
    """
    Get the user's coordinate input.

    Returns:
    (x, y) (tuple): The user's coordinate.
    """
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)


# def main():
#     """
#     The main function to receive data, get user coordinate, calculate angle and distance, and move the car.
#     """
#     global last_coordinate  # Make last_coordinate global so it can be updated

#     data = sock.recv(1024)    # Receive data from server reading 16 bytes of data
#     if data:
#         # Retrieve coordinate data from camera
#         coordinate = data.decode('utf-8')   # Decode data from byte to string

#         x_str, y_str = coordinate.split(',')
#         x_coord = int(x_str)
#         y_coord = int(y_str)
#         coordinate_int = (x_coord, y_coord)

#         # Ask the user for a new coordinate
#         new_coordinate = get_user_coordinate()
#         print("The destination coordinate: ")
#         print(new_coordinate)

#         # # Current coordinate stuff
#         # coordinate_split = coordinate.split(",")
#         # print(coordinate_split)
#         # x_coord_str = coordinate_split[0]
#         # y_coord_str = coordinate_split[1]
#         # x_coord = int(x_coord_str)
#         # y_coord = int(y_coord_str)
#         # coordinate_int = (x_coord, y_coord)
#         # print("Current Coordinate Int: ")
#         # print(coordinate_int)

#         # Calculate angle and distance to the new coordinate
#         distance = calculate_distance(coordinate_int, new_coordinate)
#         print("The distance is: ")
#         print(distance)

#         # Move the robot to the new coordinate
#         move(distance)

def main():
    """
    The main function to receive data, get user coordinate, calculate angle and distance, and move the car.
    """
    global last_coordinate  # Make last_coordinate global so it can be updated

    data = sock.recv(1024)    # Receive data from server reading 1024 bytes of data
    if data:
        # Retrieve coordinate data from camera
        data_str = data.decode('utf-8')   # Decode data from byte to string

        # Split the data by newline characters and hyphens to get each coordinate pair
        lines = re.split('\n|-', data_str)

        for line in lines:
            # Skip empty lines
            if not line:
                continue

            # Split the line into a list of components
            components = line.split(',')

            # Check if the list contains exactly two items
            if len(components) == 2:
                x_str, y_str = components
                x_coord = int(x_str)
                y_coord = int(y_str)
                coordinate_int = (x_coord, y_coord)
            else:
                print("Received unexpected coordinate format: " + line)
                # Handle unexpected coordinate format here
                continue
            
            # Ask the user for a new coordinate
            new_coordinate = get_user_coordinate()
            print("The destination coordinate: ")
            print(new_coordinate)

            print(coordinate_int)
            # Calculate angle and distance to the new coordinate
            distance = calculate_distance(coordinate_int, new_coordinate)
            print("The distance is: ")
            print(distance)

            # Move the robot to the new coordinate
            move(distance)

    
if __name__ == '__main__':
    try:
         while True:
            main()
    except KeyboardInterrupt:
         end()  

# Close the socket
sock.close()