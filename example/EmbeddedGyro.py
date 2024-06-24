# import smbus2
# from time import sleep
# import math

# # MPU6050 Registers
# PWR_MGMT_1   = 0x6B
# SMPLRT_DIV   = 0x19
# CONFIG       = 0x1A
# GYRO_CONFIG  = 0x1B
# INT_ENABLE   = 0x38
# ACCEL_XOUT_H = 0x3B
# ACCEL_YOUT_H = 0x3D
# ACCEL_ZOUT_H = 0x3F
# GYRO_XOUT_H  = 0x43
# GYRO_YOUT_H  = 0x45
# GYRO_ZOUT_H  = 0x47

# # Complementary filter
# class ComplementaryFilter:
#     def __init__(self, alpha):
#         self.alpha = alpha
#         self.angle = 0

#     def update(self, gyro_angle, accel_angle, dt):
#         self.angle = self.alpha * (self.angle + gyro_angle * dt) + (1 - self.alpha) * accel_angle
#         return self.angle

# def MPU_Init():
#     bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
#     bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
#     bus.write_byte_data(Device_Address, CONFIG, 0)
#     bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
#     bus.write_byte_data(Device_Address, INT_ENABLE, 1)

# def read_raw_data(addr):
#     high = bus.read_byte_data(Device_Address, addr)
#     low = bus.read_byte_data(Device_Address, addr+1)
#     value = ((high << 8) | low)
#     if(value > 32768):
#         value = value - 65536
#     return value

# bus = smbus2.SMBus(1)
# Device_Address = 0x68

# MPU_Init()

# print ("Reading Data of Gyroscope and Accelerometer")

# # Initialize the filter
# filter = ComplementaryFilter(alpha=0.98)

# while True:
#     #Read Accelerometer raw value
#     acc_x = read_raw_data(ACCEL_XOUT_H)
#     acc_y = read_raw_data(ACCEL_YOUT_H)
#     acc_z = read_raw_data(ACCEL_ZOUT_H)
    
#     #Read Gyroscope raw value
#     gyro_x = read_raw_data(GYRO_XOUT_H)
#     gyro_y = read_raw_data(GYRO_YOUT_H)
#     gyro_z = read_raw_data(GYRO_ZOUT_H)
    
#     # Convert gyro rate to angle
#     gyro_z_angle = gyro_z / 131.0  # Scale factor for 250 deg/s

#     # Calculate accelerometer angle (assuming only gravity influences it)
#     accel_angle = math.atan2(acc_y, acc_x)

#     # Update the filter
#     angle = filter.update(gyro_z_angle, accel_angle, 0.3)

#     print("Filtered angle: ", angle)
#     sleep(0.3)
import time
import smbus2

# MPU6050 Registers
GYRO_ZOUT_H  = 0x47
GYRO_CONFIG  = 0x1B

# Sensitivity scale factor for 2000 deg/s
sensitivity = 16.4

def read_raw_data(addr):
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)
    value = ((high << 8) | low)
    if(value > 32768):
        value = value - 65536
    return value

bus = smbus2.SMBus(1)
Device_Address = 0x68

angle = 0.0

while True:
    # Read Gyroscope raw value
    gyro_z = read_raw_data(GYRO_ZOUT_H)
    
    # Scale data to degrees per second
    scaledData = gyro_z / sensitivity
    
    # Use 1/800 for time, 800Hz sampling rate
    deltaTime = 1.0 / 800.0
    
    # (GyroData*Time) = Position
    position = scaledData * deltaTime
    
    # Accumulate position to get angle
    angle += position

    #angle %= 180


    print("Angle: ", angle)
    time.sleep(0.00125)
