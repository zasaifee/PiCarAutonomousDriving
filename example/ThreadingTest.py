import threading
from GyroKalmanFilter import readGyro  # assuming FinalGyro.py is in the same directory and has a function named Gyro
from StraightLineLoop import main as run_straight_line_loop  # assuming StraightLineLoop.py is in the same directory and has a function named main

if __name__ == '__main__':
    try:
        gyro_thread = threading.Thread(target=readGyro)
        straight_line_loop_thread = threading.Thread(target=run_straight_line_loop)

        gyro_thread.start()
        straight_line_loop_thread.start()

        gyro_thread.join()
        straight_line_loop_thread.join()
    except KeyboardInterrupt:
        print("Stopping threads...")
        # Add any cleanup code here