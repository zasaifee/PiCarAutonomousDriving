import time
import math
from picar import front_wheels
from picar import back_wheels
import picar

picar.setup()

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
fw.ready()
bw.ready()

fw.turning_max = 45

def calculate_angle(start, end):
    """
    Calculate the angle between the start point and the end point.

    Args:
        start (tuple): The start point (x, y).
        end (tuple): The end point (x, y).

    Returns:
        float: The angle in degrees.
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.degrees(math.atan2(dy, dx))
    return angle

def pivot_turn(angle_difference, angular_velocity):
    """
    Perform a pivot turn based on the desired angle.

    Args:
        angle_difference (float): The desired heading angle.
        angular_velocity (int): The speed of the turn.
    """
    if angle_difference == 0:
        end()
        return
    else:
        bw.speed = angular_velocity
        bw.left_wheel.forward()
        bw.right_wheel.backward()
        time.sleep(2)
        bw.speed = 0
        bw.stop()

def end():
    """
    Stops the robot car and turns the front wheels to 90 degrees.
    """
    bw.stop()
    fw.turn(90)

def main(start, end):
    while True:
        angle_difference = calculate_angle(start, end)
        pivot_turn(angle_difference, 50)

if __name__ == '__main__':
    try:
        start = (0, 0)  # Starting point
        end = (1, 1)  # Ending point
        while True:
            main(start, end)
    except KeyboardInterrupt:
        end()
