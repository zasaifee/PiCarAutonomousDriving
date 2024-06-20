"""
Enter a destination coordinate. The car will move for 1 second until it 
reaches the destination.

Authors: Zarin Saifee & Stephanie Torres
"""
import socket   
import time
import math
#from SunFounder_Line_Follower import Line_Follower
from picar import front_wheels
from picar import back_wheels
from datetime import datetime
import picar
import re
# Initialize the socket for communication
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.200.204.10', 12345)
#10.200.204.10  
#10.200.207.132 (zarin IP)
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

def move(coordA, coordB):
    if coordA == coordB:
        end()
        return
    else:
        bw.speed = forward_speed
        bw.forward()
        time.sleep(1.0) #travel time is 1.0 second
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



def main():
    """
    The main function to receive data, get user coordinate, calculate angle and distance, and move the car.
    """
    # Ask the user for a new coordinate
    new_coordinate = get_user_coordinate()
    print("The destination coordinate: ")
    print(new_coordinate)
    
    while True:
        data = sock.recv(1024)    # Receive data from server
        if data:
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
                    if x_str and y_str:
                        x_coord = int(x_str)
                        y_coord = int(y_str)
                        coordinate_int = (x_coord, y_coord)
                        # print("Current Coordinate Int: ")
                        # print(coordinate_int)
                else:
                    print("Received unexpected coordinate format: " + line)
                    # Handle unexpected coordinate format here
                    continue
                
                
                distance = calculate_distance(coordinate_int, new_coordinate)
                print("The current distance: ")
                print(distance)

                # update distance maybe?????
                
                time.sleep(3.0)
                move(coordinate_int, new_coordinate)
                time.sleep(3.0)

                if distance < 5:
                    end()
                    return



if __name__ == '__main__':
    try:
         while True:
            main()
    except KeyboardInterrupt:
         end()  

# Close the socket
sock.close()