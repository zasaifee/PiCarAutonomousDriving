from picar import front_wheels
from picar import back_wheels
import picar
import time

# General PiCar setup
picar.setup()

forward_speed = 50

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')

fw.ready()
bw.ready()

# Adjust the turning_offset property
#fw.turning_offset = 0  # Replace 'new_offset' with the new offset value


def move_straight():
    fw.turn_straight()  # Make sure the wheels are straight
    bw.speed = forward_speed  # Set the speed
    bw.forward()  # Start moving forward
    time.sleep(5)  # Move for 5 seconds
    bw.stop()  # Stop moving

move_straight()  # Call the function to move the robot straight forward
