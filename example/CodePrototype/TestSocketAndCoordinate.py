import socket   # Library of Low-level networking interfaces 
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

def calculate_angle_and_distance(current_coordinate, new_coordinate):
    dx = new_coordinate[0] - current_coordinate[0]
    dy = new_coordinate[1] - current_coordinate[1]
    print("dy" + str(dy))
    print("dx" + str(dx))
    distance = math.sqrt(dx**2 + dy**2)
    print("distance = " + str(distance))
    divVal = dy / dx
    angle_rad = math.atan(divVal)
    print("angle_rad = " + str(angle_rad))
    angle = math.degrees(angle_rad)
    print("degree = " + str(angle))
    # if angle < 0: 
    #     angle  = 360 + angle
    #angle = 90 - angle
    print("angle = " + str(angle))
    angle = max(55, min(135, angle))
    print("Angle bound = " + str(angle))
    return angle, distance

def move(angle, distance):
    travel_time = distance/forward_speed
    print("turning" + str(angle))
    fw.turn(angle)
    bw.speed = forward_speed
    time.sleep(5.0)     # Added . because its a float
    bw.forward()
    time.sleep(travel_time)
    print("Stopping car")

    bw.stop()
    time.sleep(5.0)  ## Added time for sleep in order have longer wait
                     ## or else it would stop and go right away 

def end():
    bw.stop()
    fw.turn(90)

def get_user_coordinate():
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)

current_coordinate = home_coordinate

# Start of data transfer 
# Receive the data in small chunks and perform your actions
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