######################################################################################################################
#  Waiting for Zarin for update on comment                                                                                                           #
######################################################################################################################
 
import time
import math
from picar import front_wheels
from picar import back_wheels
import picar
import threading
import smbus2 as smbus
import multiprocessing
from multiprocessing import Value

# MPU6050 Registers
MPU = 0x68
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Create I2C bus
bus = smbus.SMBus(1)

# Initialize variables
AccX, AccY, AccZ = 0, 0, 0
GyroX, GyroY, GyroZ = 0, 0, 0
accAngleX, accAngleY = 0, 0
gyroAngleX, gyroAngleY, gyroAngleZ = 0, 0, 0
roll, pitch, yaw = 0, 0, 0
AccErrorX, AccErrorY = 0, 0
GyroErrorX, GyroErrorY, GyroErrorZ = 0, 0, 0
elapsedTime, currentTime, previousTime = 0, time.time(), 0
c = 0

# Kalman filter variables for GyroZ
kalmanAngleZ = 0 
P_angle_z = 0 # Initialize angle 
P_bias_z = 0 # Initialize bias
Q_angle_z = 0.001 # Process noise for accelerometer
Q_bias_z = 0.003 # Process noise for gyroscope
R_measure_z = 0.03 # Measurment for noise
angle_z = 0 # angle calculated by kalman
bias_z = 0  # gyroscope bias calculate by kalman
rate_z = 0  # unbiased rate 
#yaw = Value('d', 0.0)  # 'd' is a typecode for double

# Function to read MPU6050 data
def read_mpu6050_data(register):
    high = bus.read_byte_data(MPU, register)
    low = bus.read_byte_data(MPU, register+1)
    value = ((high << 8) | low)
    if (value > 32768):
        value = value - 65536
    return value

# Function to calculate IMU error
def calculate_IMU_error():
    global AccErrorX, AccErrorY, GyroErrorX, GyroErrorY, GyroErrorZ
    c = 0
    while (c < 200):
        # Read and scale the accelerometer data below
        AccX = read_mpu6050_data(ACCEL_XOUT_H) / 16384.0
        AccY = read_mpu6050_data(ACCEL_XOUT_H+2) / 16384.0
        AccZ = read_mpu6050_data(ACCEL_XOUT_H+4) / 16384.0
        # Sum all readings

        epsilon = 1e-7
        AccErrorX = AccErrorX + ((math.atan((AccY) / (math.sqrt(math.pow((AccX), 2) + math.pow((AccZ), 2))+epsilon)) * 180 / math.pi))
        AccErrorY = AccErrorY + ((math.atan(-1 * (AccX) / (math.sqrt(math.pow((AccY), 2) + math.pow((AccZ), 2))+ epsilon)) * 180 / math.pi))
        c += 1
    # Divide the sum by 200 to get the error value
    AccErrorX = AccErrorX / 200
    AccErrorY = AccErrorY / 200
    c = 0
    # Read gyro values 200 times
    while (c < 200):
        # Read and scale gyroscope data 
        GyroX = read_mpu6050_data(GYRO_XOUT_H) / 131.0
        GyroY = read_mpu6050_data(GYRO_XOUT_H+2) / 131.0
        GyroZ = read_mpu6050_data(GYRO_XOUT_H+4) / 131.0
        # Sum all readings
        GyroErrorX = GyroErrorX + GyroX
        GyroErrorY = GyroErrorY + GyroY
        GyroErrorZ = GyroErrorZ + GyroZ
        c += 1
    # Divide the sum by 200 to get the error value
    GyroErrorX = GyroErrorX / 200
    GyroErrorY = GyroErrorY / 200
    GyroErrorZ = GyroErrorZ / 200


def readGyro():
    global currentTime, GyroX, GyroY, GyroZ, bias_z, angle_z, P_angle_z, P_bias_z, Q_angle_z, gyroAngleX, gyroAngleY, accAngleX, accAngleY, roll, pitch
    while True:
        # === Read accelerometer data === //
        # Read and scale the accelerometer data
        AccX = read_mpu6050_data(ACCEL_XOUT_H) / 16384.0
        AccY = read_mpu6050_data(ACCEL_XOUT_H+2) / 16384.0
        AccZ = read_mpu6050_data(ACCEL_XOUT_H+4) / 16384.0

        # Calculating Roll and Pitch from the accelerometer data
        accAngleX = (math.atan(AccY / math.sqrt(math.pow(AccX, 2) + math.pow(AccZ, 2))) * 180 / math.pi) - 0.58
        accAngleY = (math.atan(-1 * AccX / math.sqrt(math.pow(AccY, 2) + math.pow(AccZ, 2))) * 180 / math.pi) + 1.58

        # === Read gyroscope data === //
        previousTime = currentTime 
        currentTime = time.time()
        elapsedTime = currentTime - previousTime
        # Read and scale the gyroscope data
        GyroX = read_mpu6050_data(GYRO_XOUT_H) / 131.0
        GyroY = read_mpu6050_data(GYRO_XOUT_H+2) / 131.0
        GyroZ = read_mpu6050_data(GYRO_XOUT_H+4) / 131.0

        # Correct the outputs with the calculated error values
        GyroX = GyroX + 0.56
        GyroY = GyroY - 2
        GyroZ = GyroZ + 0.01

        # Kalman filter for GyroZ
        rate_z = GyroZ - bias_z  # Calculate the unbiased rate
        angle_z += elapsedTime * rate_z  # Update the angle estimate

        # Prediction step
        P_angle_z += elapsedTime * (2*P_bias_z - elapsedTime*Q_angle_z) # Update angle
        P_bias_z -= elapsedTime * P_bias_z # Update bias 
        P_bias_z += Q_bias_z * elapsedTime # Add the process noise 

        # Since there's no direct measurement for yaw angle, we skip the update step for GyroZ

        # Currently the raw values are in degrees per seconds, deg/s, so we need to multiply by seconds (s) to get the angle in degrees
        gyroAngleX = gyroAngleX + GyroX * elapsedTime # Update gyroscope x angle
        gyroAngleY = gyroAngleY + GyroY * elapsedTime # Update gyroscope y angle
        yaw =  angle_z  # Use the angle estimated by the Kalman filter

        # Complementary filter - combine accelerometer and gyro angle values
        roll = 0.96 * gyroAngleX + 0.04 * accAngleX
        pitch = 0.96 * gyroAngleY + 0.04 * accAngleY

        # Print the values
        # print("Roll: ", roll, " Pitch: ", pitch, " Yaw: ", yaw)
        #print(yaw)

        file2 = open("/home/raspberrypi/PiCarAutonomousDriving/example/yawData.txt", "a+")
        yawData = str(yaw)
        file2.write(yawData)
        file2.write("\n")
        file2.close()

        time.sleep(0.10)


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
bus.write_byte_data(MPU, 0x6B, 0x00)
print("gyro initialized")

time.sleep(2)

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

def run():
    while True:
        angle = calculate_angle([67, -13],[100, -160])
        print("angle: ")
        print(angle)

        diff = angle-yaw
        print("diff: ")
        print(diff)
        
        if(diff < 10):
            end()
            return
        pivot_turn()

def main():

        readGyro_process = multiprocessing.Process(target=readGyro)
        readGyro_process.start()

        time.sleep(1)

        angle = calculate_angle([76, 11],[241, 154])

        angle = abs(angle)

        with open("/home/raspberrypi/PiCarAutonomousDriving/example/yawData.txt", "r") as file:
            lines = file.readlines()
            yaw = float(lines[-1].strip())  # Get the last line in the file
            #print(yaw)
        
        diff = angle-yaw

        while(diff > 10):
            diff = angle-yaw
            print(yaw)
            print(diff)
            pivot_turn()
            with open("/home/raspberrypi/PiCarAutonomousDriving/example/yawData.txt", "r") as file:
                lines = file.readlines()
                yaw = float(lines[-1].strip())  # Update the yaw value
        end()

     

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        end()