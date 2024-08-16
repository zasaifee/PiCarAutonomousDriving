"""
Enter a destination coordinate. The car will pivot turn to the destination coordinate and then 
move forward towards the coordinate.

Authors: Zarin Saifee & Stephanie Torres
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
home_coordinate = (-192,165)

def calculate_angle_and_distance(current_coordinate, new_coordinate):
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
    angle_rad = math.atan2(dy, dx)
    angle = math.degrees(angle_rad)
    return angle, distance

def pivot_turn():
    """
    Perform a pivot turn.
    """
    bw.speed = 45
    bw.left_wheel.backward()
    bw.right_wheel.forward()
    time.sleep(10.0)
    bw.speed = 0
    bw.stop()

def timeCalc(angle):
    turning_time = abs(angle)*0.05
    print("Turning Time: " + str(turning_time))

def move():
    """
    Move the car based on the given angle and distance.

    Parameters:
    angle (float): The angle to turn.
    distance (float): The distance to move.
    """

    bw.speed = 45
    bw.forward()
    time.sleep(5.0)
    bw.speed = 0
    bw.stop()

def end():
    """
    Stop the car and turn the front wheels straight.
    """
    bw.stop()
    fw.turn(90)


# Define the current coordinate
current_coordinate = home_coordinate

def main():
    move()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
         end()  