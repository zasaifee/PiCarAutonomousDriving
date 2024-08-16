#######################################################################################################
# This code is the overall multiprocessing use in order to use the Gyro(MPU6050) and in this case     #
#  use the StraightLineLoop code in order to test if it is correctly being used. In which it was      #
#  working as it should after a few minor testing changes.                                            #
#                                                                                                     #
#  References:                                                                                        #
#     1.                                                                                              #
#                                                                                                     #
#  Author:  Zarin Saifee                                                                              #
#######################################################################################################

import multiprocessing
import Gryo_Multiprocessing
import StraightLineLoop

def run_gyro(yaw):
    # Call the function that starts the gyroscope
    Gryo_Multiprocessing.readGyro(yaw)

def run_straight_line_loop(x_coordinate, y_coordinate, yaw):
    # Call the function that starts the straight line loop
    StraightLineLoop.main(x_coordinate, y_coordinate, yaw)

if __name__ == "__main__":
    # Create a shared double precision number for yaw
    yaw = multiprocessing.Value('d', 0.0)

    x_coordinate = float(input("Enter the x-coordinate: "))
    y_coordinate = float(input("Enter the y-coordinate: "))

    # Create processes
    p1 = multiprocessing.Process(target=run_gyro, args=(yaw,))
    p2 = multiprocessing.Process(target=run_straight_line_loop, args=(x_coordinate, y_coordinate, yaw))

    # Start processes
    p1.start()
    p2.start()

    # Join processes to the main process
    p1.join()
    p2.join()