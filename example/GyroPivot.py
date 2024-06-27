import socket   
import time
import math as math
import FinalGyro as gyro
from picar import front_wheels
from picar import back_wheels
import picar
import re
import numpy as np

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
    Gets the current heading angle of the robot car.

    Returns:
        float: Current heading angle (in radians)
    """
    heading_angle = gyro.yaw
    return heading_angle

def calculate_distance(current_coordinate, new_coordinate):
    """
    Calculates the y-axis distance between two coordinates.

    Args:
        current_coordinate (tuple): Current (x, y) coordinate.
        new_coordinate (tuple): New (x, y) coordinate.

    Returns:
        float: Difference between y-coordinates.
    """
    dx = new_coordinate[0] - current_coordinate[0]
    dy = new_coordinate[1] - current_coordinate[1]
    
    distance = math.sqrt(dx**2 + dy**2)
    return distance

def calculate_angle(coordA, coordB):
    """
    Calculates the angle between two coordinates.

    Args:
        coordA (tuple): Starting (x, y) coordinate.
        coordB (tuple): Target (x, y) coordinate.

    Returns:
        float: Angle in degrees.
    """
    # Convert coordinates to numpy arrays

def unicycleDynamics(X, U):
    """
    Args: X, U
            X = Starting point array. [X_0, Y_0, theta_0] - (x,y) and starting angle with respect to x-axis
            U = Destination Point Array. [U_x,U_y, U_theta] - (x,y), the U_theta is not relevent in this code 
            as the element is not used at any point but it needs to be included to calculate the norm 

    Return: v, w
            v = forward_velocity
            w = angular_velocity
    """
    X = np.array(X)
    U = np.array(U)
    e = U-X
    E = np.linalg.norm(e)
    dx = U[0] - X[0]
    dy = U[1] - X[1]
    phi = math.atan2(dy, dx) - X[2]
    v = E* math.cos(phi)
    w = ((math.cos(phi) + 1) * math.sin(phi))+ phi

    print(v)
    print(w)
    return v,w
   
def pivot_turn(angle_difference):
    """
    Perform a pivot turn based on the desired angle.

    Args:
        desired_angle (float): The desired heading angle.
    """

    if angle_difference == 0:
        end()
        return
    else:
        bw.speed = 45
        bw.left_wheel.forward()
        bw.right_wheel.backward()
        time.sleep(0.1)
        bw.speed = 0
        bw.stop()


def move_straight(coordA, coordB):
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
    still_turning = 1
    gyro.Gyro() #Turn on and start monitoring the angle the car is facing

    
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



                desired_heading_angle = calculate_angle(coordinate_int, new_coordinate)
                current_heading_angle = get_current_heading_angle()
                angle_difference = desired_heading_angle - current_heading_angle
                if angle_difference <= 10:
                    end()
                    still_turning = 0
                else:
                    time.sleep(1.0)
                    pivot_turn(angle_difference)

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