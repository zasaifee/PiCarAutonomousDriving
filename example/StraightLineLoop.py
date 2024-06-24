"""
This script controls a robot car using socket communication to receive coordinate data.
It connects to a server at a specified IP address and port, receives coordinate updates,
and moves the car toward the target coordinate until it reaches within a certain distance.

Author: Stephanie Torres and Zarin Saifee

Usage:
1. Make sure the server is running and providing coordinate data.
2. Adjust the server address and port in the 'server_address' variable.
3. Run this script to control the robot car.

Dependencies:
- picar library (install using 'pip install picar')

Note: Replace the placeholder IP addresses with the actual server IP addresses.

"""
import socket   
import time
import math
from picar import front_wheels
from picar import back_wheels
from datetime import datetime
import picar
import re

# Initialize the socket for communication
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.200.204.10', 12345)
# Stephanie's IP Address: 10.200.204.10
# Zarin's IP Address: 10.200.207.132 

sock.connect(server_address)    

last_coordinate = None  

picar.setup()


# Initialize robot car parameters
forward_speed = 50
backward_speed = 35

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
fw.ready()
bw.ready()

fw.turning_max = 45


def calculate_distance(current_coordinate, new_coordinate):
    """
    Calculates the Euclidean distance between two coordinates.

    Args:
        current_coordinate (tuple): Current (x, y) coordinate.
        new_coordinate (tuple): New (x, y) coordinate.

    Returns:
        float: Euclidean distance.
    """
    dx = new_coordinate[0] - current_coordinate[0]
    # dy = new_coordinate[1] - current_coordinate[1]
    dy = current_coordinate[1] - new_coordinate[1]

    distance = math.sqrt(dx**2 + dy**2)
    return dy

def move(coordA, coordB):
    """
    Moves the robot car from coordA to coordB.

    Args:
        coordA (tuple): Starting (x, y) coordinate.
        coordB (tuple): Target (x, y) coordinate.
    """
    if coordA == coordB:
        end()
        return
    else:
        bw.speed = forward_speed
        bw.forward()
        time.sleep(0.25) 
        bw.speed = 0
        bw.stop()
    

def end():
    """
    Stops the robot car and turns the front wheels to 90 degrees.
    """
    bw.stop()
    fw.turn(90)

def get_user_coordinate():
    """
    Gets user input for a new coordinate.

    Returns:
        tuple: User-specified (x, y) coordinate.
    """
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)


def main():
    """
    Main function to control the robot car based on received coordinate data.
    """
    new_coordinate = get_user_coordinate()
    print("The destination coordinate: ")
    print(new_coordinate)
    prev_distance = 0
    distance = 0
    
    while True:
        data = sock.recv(1024)    
        if data:
            data_str = data.decode('utf-8')   

            lines = re.split('\n|-', data_str)

            for line in lines:
                if not line:
                    continue

                components = line.split(',')

                if len(components) == 2:
                    x_str, y_str = components
                    if x_str and y_str:
                        x_coord = int(x_str)
                        y_coord = int(y_str)
                        coordinate_int = (x_coord, y_coord)
                        print("Current Coordinate Int: ")
                        print(coordinate_int)
                else:
                    continue

                distance = calculate_distance(coordinate_int, new_coordinate)
                print("The current distance: ")
                print(distance)

                if distance <= 10:
                    end()
                    return
                
                time.sleep(1.0)
                move(coordinate_int, new_coordinate)

                prev_distance = distance
                print(prev_distance)

if __name__ == '__main__':
    try:
         while True:
            main()
    except KeyboardInterrupt:
         end()  

sock.close()