"""
Autonomous Driving Code for Robot Car - 

-------------------------------------------------------------------------------------------------------
NOT FUNCTIONAL - NEED MULTIPROCESSING OR THREADING
-------------------------------------------------------------------------------------------------------

This script controls a robot car to autonomously navigate to a user-defined destination coordinate.
It uses gyro data for heading angle, socket communication for real-time updates, and unicycle dynamics for motion control.

Authors: Zarin Saifee & Stephanie Torres
Date: July 2024

"""

import socket
import time
import math
import sys
from picar import front_wheels, back_wheels
from GyroFiles import GyroKalmanFilter_Origional as gyro
from CodePrototype import UnicycleDynamics as ud

# Initialize the socket for communication
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.200.204.10', 12345)
sock.connect(server_address)

picar.setup()

# Initialize robot car parameters
forward_speed = 50
backward_speed = 35

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
fw.ready()
bw.ready()

fw.turning_max = 45

def get_current_heading_angle():
    """
    Get the current heading angle from the gyro.

    Returns:
        float: Current heading angle in degrees.
    """
    heading_angle = gyro.yaw
    print(heading_angle)
    return heading_angle

def calculate_distance(current_coordinate, new_coordinate):
    """
    Calculate the Euclidean distance between two coordinates.

    Args:
        current_coordinate (tuple): Current (x, y) coordinate.
        new_coordinate (tuple): New (x, y) coordinate.

    Returns:
        float: Distance between the two coordinates.
    """
    dx = new_coordinate[0] - current_coordinate[0]
    dy = new_coordinate[1] - current_coordinate[1]
    distance = math.sqrt(dx**2 + dy**2)
    return distance

def pivot_turn(angle_difference, angular_velocity):
    """
    Perform a pivot turn based on the angle difference.

    Args:
        angle_difference (float): Difference between desired and current heading angle.
        angular_velocity (float): Angular velocity for the turn.
    """
    if angle_difference == 0:
        end()
    else:
        bw.speed = angular_velocity
        bw.left_wheel.forward()
        bw.right_wheel.backward()
        time.sleep(0.1)
        bw.speed = 0
        bw.stop()

def move_straight(coordA, coordB):
    """
    Move straight from coordA to coordB.

    Args:
        coordA (tuple): Starting (x, y) coordinate.
        coordB (tuple): Destination (x, y) coordinate.
    """
    if coordA == coordB:
        end()
    else:
        bw.speed = forward_speed
        bw.forward()
        time.sleep(0.25)
        bw.speed = 0
        bw.stop()

def end():
    """Stop the robot car and turn the front wheels to 90 degrees."""
    bw.stop()
    fw.turn(90)

def get_user_coordinate():
    """
    Get user-defined destination coordinate.

    Returns:
        tuple: (x, y) coordinate.
    """
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)

def main():
    """
    Main function for autonomous navigation.

    1. Gets user-defined destination coordinate.
    2. Reads gyro data for heading angle.
    3. Receives real-time updates via socket communication.
    4. Calculates angle difference and distance.
    5. Executes pivot turns and straight movements accordingly.
    """
    new_coordinate = get_user_coordinate()
    print("The destination coordinate: ")
    print(new_coordinate)
    prev_distance = 0
    distance = 0
    still_turning = 1

    x_coord, y_coord = 0, 0
    coordinate_int = (x_coord, y_coord)

    while True:
        gyro.readGyro()

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

                current_heading_angle = get_current_heading_angle() + 90
                current_heading_angle = math.radians(current_heading_angle)
                xCoord = (x_coord, y_coord, current_heading_angle)
                uCoord = (new_coordinate[0], new_coordinate[1], 0)

                v, w, phi = ud.unicycleDynamics(xCoord, uCoord)
                angle_difference = phi - current_heading_angle

                if angle_difference <= 10:
                    end()
                    still_turning = 0
                else:
                    time.sleep(1.0)
                    pivot_turn(angle_difference, w)

                if still_turning == 0:
                    distance = calculate_distance(coordinate_int, new_coordinate)

                    print("The current distance: ")
                    print(distance)
                    if distance <= 10:
                        end()
                        return
                    time.sleep(1.0)
                    move_straight(coordinate_int, new_coordinate)
                    prev_distance = distance
                    print(prev_distance)

if __name__ == '__main__':
    try:
         while True:
            main()
    except KeyboardInterrupt:
         end()  

sock.close()