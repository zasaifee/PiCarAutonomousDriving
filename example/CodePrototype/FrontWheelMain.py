"""
PiCar Autonomous Driving Script

This script sets up a PiCar to receive coordinates from a remote server and move to the specified coordinates.
It uses a TCP socket to communicate with the server and calculates the angle and distance to move the car.

Modules:
    - socket: Library of low-level networking interfaces
    - time: Time access and conversions
    - math: Mathematical functions
    - os: Miscellaneous operating system interfaces
    - sys: System-specific parameters and functions
    - Line_Follower: Line following module for PiCar
    - picar: PiCar control module
    - front_wheels: Front wheels control module
    - back_wheels: Back wheels control module


Authors: Zarin Saifee & Stephanie Torres
Date: July 2024
"""

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

# Create socket object (IP address for IPv4, Indicate we are using TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server's address and port
server_address = ('10.200.207.132', 12345)  # Use laptop IP
sock.connect(server_address)    # Establish the connection to remote server

last_coordinate = None  # Variable to store last received coordinate

# General PiCar setup
picar.setup()

forward_speed = 50
backward_speed = 35

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')

fw.ready()
bw.ready()
fw.turning_max = 45

home_coordinate = (-192, 165)

def calculate_angle_and_distance(current_coordinate, new_coordinate):
    """
    Calculate the angle and distance between two coordinates.

    Args:
        current_coordinate (tuple): The current coordinate (x, y).
        new_coordinate (tuple): The new coordinate (x, y).

    Returns:
        tuple: The angle (in degrees) and distance between the coordinates.
    """
    dx = new_coordinate[0] - current_coordinate[0]
    dy = new_coordinate[1] - current_coordinate[1]
    distance = math.sqrt(dx**2 + dy**2)
    angle_rad = math.atan2(dy, dx)
    angle = math.degrees(angle_rad)
    
    return angle, distance

def move(angle, distance):
    """
    Move the PiCar to a new coordinate based on the given angle and distance.

    Args:
        angle (float): The angle to turn (in degrees).
        distance (float): The distance to travel.
    """
    # Calculate the time it takes to travel the given distance at the forward speed
    travel_time = distance / forward_speed
    print("Travel time: " + str(travel_time))

    # Calculate the turning rate based on the forward speed and the maximum turning rate
    turning_rate = forward_speed / fw.turning_max
    print("Turning rate: " + str(turning_rate))

    # Calculate the time it takes to turn the given angle at the turning rate
    turning_time = abs(angle) / turning_rate
    print("Turning time: " + str(turning_time))

    # If the angle is positive, turn left
    if angle > 0:
        print("Turning left: " + str(angle))
        fw.turn_left()
    # If the angle is negative, turn right
    elif angle < 0:
        print("Turning right: " + str(angle))
        fw.turn_right()

    # Set the backward speed to the forward speed
    bw.speed = forward_speed

    # Wait for the turning time, then stop
    time.sleep(turning_time)
    bw.stop()

    # Wait for 1 second
    time.sleep(1.0)

    # Turn straight
    fw.turn_straight()

    # Move forward
    bw.forward()

    # Wait for the travel time, then stop
    time.sleep(travel_time)
    bw.stop()

    # Wait for 5 seconds
    time.sleep(5.0)

def end():
    """
    Stop the PiCar and reset the front wheels to the default position.
    """
    bw.stop()
    fw.turn(90)

def get_user_coordinate():
    """
    Get a new coordinate from the user.

    Returns:
        tuple: The new coordinate (x, y).
    """
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)

current_coordinate = home_coordinate


def main():
    """
    Main function to handle data transfer and movement of the PiCar.
    """
    # Start of data transfer
    # Receive the data in small chunks and perform your actions
    data = sock.recv(16)  # Receive data from server reading 16 bytes of data
    if data:  # If data received
        coordinate = data.decode('utf-8')  # Decode data from byte to string
        print('Current coordinate: {!r}'.format(coordinate))  # r! convert value to string

        # Ask the user for a new coordinate
        new_coordinate = get_user_coordinate()
        print(new_coordinate)

        print("Current Coord: ")
        print(current_coordinate)
        
        # Calculate angle and distance to the new coordinate
        angle, distance = calculate_angle_and_distance(current_coordinate, new_coordinate)
        
        # Move the robot to the new coordinate
        move(angle, distance)

        print(angle)
        print(distance)



if __name__ == '__main__':
    try:
         while True:
             main()
    except KeyboardInterrupt:
         end()  
# After all is done
sock.close()
