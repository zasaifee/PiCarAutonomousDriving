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
server_address = ('10.200.207.224', 12345)  # Use laptop IP
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

# Start of data transfer 
# Receive the data in small chunks and perform your actions
while True:
    data = sock.recv(16)    # Recieve data from server reading 16 bytes of data
    if data:    # If data recieved
        coordinate = data.decode('utf-8')   # Decode data from byte to string
        print('received {!r}'.format(coordinate))   # r! convert value to string
        # Check if the coordinate has changed
        if coordinate != last_coordinate:
            print('Coordinate change detected!')
            last_coordinate = coordinate
    else:
        break

#After all is done
sock.close()