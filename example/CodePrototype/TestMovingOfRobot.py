#!/usr/bin/env python
'''
**********************************************************************
* Filename    : Test1
* Description : Testing movement of the car
* Author      : Zarin
**********************************************************************
'''
##################################################################################################
#  imports for front and back wheel configurations and line follower stuff (unsure if needed)    #
################################################################################################## 
import os
import sys
sys.path.insert(0, os.path.abspath('/home/raspberrypi/PiCarAutonomousDriving/example/Original_RaspberryPi_Code/SunFounder_Line_Follower'))
import Line_Follower
from picar import front_wheels
from picar import back_wheels
import time
import picar


#####################################################################################################################
#   General PiCar setup (file is lowkey confusing), setting speeds and assigning front/back wheels to variables     #
#   calling ready() function to calibrate and ensure the wheels are "ready" for use                                 #            
#   setting maximum turning angle to 45                                                                             #
#####################################################################################################################
picar.setup()

forward_speed = 50
backward_speed = 35

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')

fw.ready()
bw.ready()
fw.turning_max = 45

#############################################################################################################
#   go_straight() makes the back wheels have a standard speed of 75, it should use the function forward()   # 
#   to move both back wheels in the forward direction and turn the front wheels to face forward             #
#############################################################################################################
def go_straight():
    while True:
        bw.speed = 75
        bw.forward()
        fw.turn_straight()
        time.sleep(0.2)
        bw.stop()
################################################################
#   turn the forward wheels right by whatever angle is given   # 
################################################################
def turn_right(angle):
     fw.turn(angle)


#########################################################################################################################
#   move() moves the car based on the given angle and distance. using the provided distance, it calculates the time it  #
#   needs to travel. it then turns the front wheels based on the provided angle, and moves for the calculated time at   #
#   at the specified angle.                                                                                             #
#########################################################################################################################
def move(angle, distance):
     travel_time = distance/forward_speed
     print("turning" + str(angle))
     turn_right(angle)
     bw.speed = forward_speed
     time.sleep(5.0)     # Added . because its a float
     bw.forward()
     time.sleep(travel_time)
     print("Stopping car")
     bw.stop()
     time.sleep(5.0)  ## Added time for sleep in order have longer wait
                      ## or else it would stop and go right away 

#####################################################################################################
#   set the speed of the backwheels to be speed you want the car to move in the foward direction    #
#   have the car move foward                                                                        #   
#####################################################################################################
def main():
        move(120,10)

########################
#   stop the program   #
########################
def end():
	bw.stop()
	fw.turn(90)

#################
#   run main    #
#################
if __name__ == '__main__':
    try:
        while True:  
            main()
    except KeyboardInterrupt:
         end()