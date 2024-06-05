import socket   # Library of Low-level networking interfaces 
import time
import math
from SunFounder_Line_Follower import Line_Follower
from picar import front_wheels
from picar import back_wheels
import picar

# Create socket object (IP address for IPv4, Indicate we are using TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server's address and port
server_address = ('10.200.207.132', 12345)  # Use laptop IP
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

home_coordinate = (-192,165)


def calculate_angle_and_distance(current_coordinate, new_coordinate):
    dx = new_coordinate[0] - current_coordinate[0]
    dy = new_coordinate[1] - current_coordinate[1]
    distance = math.sqrt(dx**2 + dy**2)
    angle_rad = math.atan2(dy, dx)
    angle = math.degrees(angle_rad)
    # if(angle < 0) : angle  = angle + 360
    
    return angle, distance

def pivot_turn():
    # radius = 20
    # speed = forward_speed
    # distance = radius * angle
    # turn_time = distance / speed
    # bw.speed = 50
    # bw.pivotRight()
    # time.sleep(turn_time)

    bw.speed = 50
    bw.left_wheel.forward()
    bw.right_wheel.backward()



def move(angle, distance):
    # Calculate the time it takes to travel the given distance at the forward speed
    travel_time = distance/forward_speed
    turning_time = abs(angle)*0.05

    print("Travel time: " + str(travel_time))

    # Calculate the turning rate based on the forward speed and the maximum turning rate
    # Wait for 1 second

    pivot_turn()
    time.sleep(turning_time)
    bw.stop()
    time.sleep(2.0)

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
    bw.stop()
    fw.turn(90)

def get_user_coordinate():
    x = float(input("Enter the x-coordinate: "))
    y = float(input("Enter the y-coordinate: "))
    return (x, y)

current_coordinate = home_coordinate

# Start of data transfer 
# Receive the data in small chunks and perform your actions

def main():
    data = sock.recv(16)    # Recieve data from server reading 16 bytes of data
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

   



if __name__ == '__main__':
    try:
         while True:
             main()
    except KeyboardInterrupt:
         end()

         
#After all is done
sock.close()
        


