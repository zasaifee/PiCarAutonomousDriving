import smbus2 as smbus
import time
import math

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
        AccX = read_mpu6050_data(ACCEL_XOUT_H) / 16384.0
        AccY = read_mpu6050_data(ACCEL_XOUT_H+2) / 16384.0
        AccZ = read_mpu6050_data(ACCEL_XOUT_H+4) / 16384.0
        # Sum all readings
        AccErrorX = AccErrorX + ((math.atan((AccY) / math.sqrt(math.pow((AccX), 2) + math.pow((AccZ), 2))) * 180 / math.pi))
        AccErrorY = AccErrorY + ((math.atan(-1 * (AccX) / math.sqrt(math.pow((AccY), 2) + math.pow((AccZ), 2))) * 180 / math.pi))
        c += 1
    # Divide the sum by 200 to get the error value
    AccErrorX = AccErrorX / 200
    AccErrorY = AccErrorY / 200
    c = 0
    # Read gyro values 200 times
    while (c < 200):
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

# Initialize MPU6050
bus.write_byte_data(MPU, 0x6B, 0x00)

# Call this function if you need to get the IMU error values for your module
calculate_IMU_error()

while True:
    # === Read accelerometer data === //
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
    GyroX = read_mpu6050_data(GYRO_XOUT_H) / 131.0
    GyroY = read_mpu6050_data(GYRO_XOUT_H+2) / 131.0
    GyroZ = read_mpu6050_data(GYRO_XOUT_H+4) / 131.0
    # Correct the outputs with the calculated error values
    GyroX = GyroX + 0.56
    GyroY = GyroY - 2
    GyroZ = GyroZ + 0.01
    #Changing the GyroZ to add to 0.01 seemed to make the increase of the yaw drift
    # take longer time to increase by 1. For now this is a an alternative till I impliment 
    # a drift supressor.
    
    # Currently the raw values are in degrees per seconds, deg/s, so we need to multiply by seconds (s) to get the angle in degrees
    gyroAngleX = gyroAngleX + GyroX * elapsedTime
    gyroAngleY = gyroAngleY + GyroY * elapsedTime
    yaw =  yaw + GyroZ * elapsedTime
    # Complementary filter - combine accelerometer and gyro angle values
    roll = 0.96 * gyroAngleX + 0.04 * accAngleX
    pitch = 0.96 * gyroAngleY + 0.04 * accAngleY
    # Print the values
    print("Roll: ", roll, " Pitch: ", pitch, " Yaw: ", yaw)
    time.sleep(0.10)
