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
import picar
import ast

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
    time.sleep(1.0)
    bw.speed = 45
    bw.left_wheel.backward()
    bw.right_wheel.forward()

def move(angle, distance):
    """
    Move the car based on the given angle and distance.

    Parameters:
    angle (float): The angle to turn.
    distance (float): The distance to move.
    """
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

# Define the current coordinate
current_coordinate = home_coordinate

def main():
    """
    The main function to receive data, get user coordinate, calculate angle and distance, and move the car.
    """
    data = sock.recv(16)    # Recieve data from server reading 16 bytes of data
    if data:
        coordinate = data.decode('utf-8')   # Decode data from byte to string

        
        #print('Current coordinate string: {!r}'.format(coordinate))   # r! convert value to string
        coordinate_split = coordinate.split(",")
        x_coord_str = coordinate_split[0]
        y_coord_str = coordinate_split[1]
        x_coord = int(x_coord_str)
        y_coord = int(y_coord_str)
        coordinate_int = (x_coord, y_coord)
        print("Current Coordinate Int: ")
        print(coordinate_int)

        print("Current Coordinate: ")
        print(current_coordinate)

            # Ask the user for a new coordinate
        new_coordinate = get_user_coordinate()
        print(new_coordinate)

        print("Current Coord: ")    
        print(current_coordinate)

        
        
            
        # Calculate angle and distance to the new coordinate
        angle, distance = calculate_angle_and_distance(coordinate_int, new_coordinate)
            
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

# Close the socket
sock.close()