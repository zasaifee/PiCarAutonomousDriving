
""""
Enter a destination coordinate. The car will pivot turn to the destination coordinate and then 
move forward towards the coordinate.

Authors: Zarin Saifee & Stephanie Torres
"""
import socket   
import time
import math
from picar import front_wheels
from picar import back_wheels
import picar
import smbus					#import SMBus module of I2C
from time import sleep          #import

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
#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

print (" Reading Data of Gyroscope and Accelerometer")


def ReadData(): 
	while True:
		
		#Read Accelerometer raw value
		acc_x = read_raw_data(ACCEL_XOUT_H)
		acc_y = read_raw_data(ACCEL_YOUT_H)
		acc_z = read_raw_data(ACCEL_ZOUT_H)
		
		#Read Gyroscope raw value
		gyro_x = read_raw_data(GYRO_XOUT_H)
		gyro_y = read_raw_data(GYRO_YOUT_H)
		gyro_z = read_raw_data(GYRO_ZOUT_H)
		
		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		Ax = acc_x/16384.0
		Ay = acc_y/16384.0
		Az = acc_z/16384.0
		
		Gx = gyro_x/131.0
		Gy = gyro_y/131.0
		Gz = gyro_z/131.0
		

		print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az) 	
		sleep(0.3)


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