import time
import math
from picar import front_wheels
from picar import back_wheels
import picar
import threading
import GyroKalmanFilter as gyro

print("STARTTT")

picar.setup()
print("picar setup")

fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
fw.ready()
bw.ready()
print("wheels initialized")

fw.turning_max = 45

# Initialize MPU6050
gyro.bus.write_byte_data(gyro.MPU, 0x6B, 0x00)
print("gyro initialized")

time.sleep(2)


# Call this function if you need to get the IMU error values for your module
gyroCalc_thread = threading.Thread(target = gyro.calculate_IMU_error)
gyroCalc_thread.start()
print("imu error running")

readGyro_thread = threading.Thread(target=gyro.readGyro)
readGyro_thread.start()
print("read gyro running")

def calculate_angle(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.degrees(math.atan2(dy, dx))
    return angle

def pivot_turn():

    bw.speed = 50
    bw.left_wheel.forward()
    bw.right_wheel.backward()
    time.sleep(0.25)
    bw.speed = 0
    bw.stop()

def end():
    bw.stop()
    fw.turn(90)

def main():
    while True:
        gyro_reading = gyro.yaw
        print(gyro_reading)
        # if ( gyro_reading < 10):
        #     end()
        #     return
        # pivot_turn()

if __name__ == '__main__':
    try:
        print(gyro.yaw)
        main()
    except KeyboardInterrupt:
        end()