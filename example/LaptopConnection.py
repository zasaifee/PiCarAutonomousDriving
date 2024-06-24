"""
This script uses a webcam to track QR codes, calculates their coordinates, and writes them 
to a text file. It also encodes this data and sends it over a network using a TCP socket server. 
The video feed is displayed with a crosshair, a line to the detected QR code, and the distances 
from the crosshair to the QR code. The script runs continuously until ‘q’ is pressed.

Author: Daniel Lee
Edited By: Zarin Saifee and Stephanie Torres
"""

import cv2
import cv2.aruco as aruco
import socket

"""
Lines 15-31 are dedicated to the creation of a socket and the establishment of the camera. 
This process is crucial for forming a connection between the laptop and the Raspberry Pi car. 

The key components involved in this process include:
    1. The IP address of your laptop, which can be located within your network settings.
    2. The use of port '12345', which essentially functions as a password to ensure a secure connection to the correct device.
    3. The sock.listen(1) command, which indicates that we are focusing on establishing a single connection to the Raspberry Pi, hence the argument ‘1’.

"""
# Initialize the camera
vid_capture = cv2.VideoCapture(0)  # Change the value '0' according to which USB connection for your computer
screenWidth = int(vid_capture.get(3))
screenHeight = int(vid_capture.get(4))

# Create socket object (IP address for IPv4, Indicate we are using TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('10.200.204.10', 12345)   # Use laptop's IP
sock.bind(server_address)   # Bind the socket to IP & Port to receive connections

# Listen for incoming connections
sock.listen(1)

# New socket to communicate with clinet 
connection, client_address = sock.accept()
print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

if not vid_capture.isOpened():
    print("Error opening webcam!")
else:
    # Define the ArUco dictionary and parameters
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    aruco_params = aruco.DetectorParameters()
    while vid_capture.isOpened():
        ret, frame = vid_capture.read()
        if ret:
            # Calculate the center of the crosshair
            crosshair_x, crosshair_y = int(screenWidth / 2), int(screenHeight / 2)
            # Detect ArUco markers in the frame
            corners, ids, _ = aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)
            cv2.line(frame, (crosshair_x, crosshair_y - 10), (crosshair_x, crosshair_y + 10), (0, 255, 0), 2)  # crosshair
            cv2.line(frame, (crosshair_x - 10, crosshair_y), (crosshair_x + 10, crosshair_y), (0, 255, 0), 2)  # crosshair
            if ids is not None:
                # Find the marker with ID 10
                for i in range(len(ids)):
                    if ids[i] == 10:
                        # Draw the detected marker
                        aruco.drawDetectedMarkers(frame, corners)
                        # Calculate the center of the detected marker
                        marker_center_x = int((corners[i][0][0][0] + corners[i][0][2][0]) / 2)
                        marker_center_y = int((corners[i][0][0][1] + corners[i][0][2][1]) / 2)
                        # Draw a line from the crosshair to the marker
                        cv2.line(frame, (crosshair_x, crosshair_y), (marker_center_x, marker_center_y), (255, 0, 0), 2)
                        # Calculate distances with proper sign
                        dist_x = marker_center_x - crosshair_x
                        dist_y = marker_center_y - crosshair_y

                        """
                        Lines 77-93 is primarily concerned with writing coordinate data to a file named ‘cameracoords.txt’ and 
                        transmitting the X coordinate and Y coordinate data from the laptop to the Raspberry Pi.
                        """
                        # writing coordinates to file cameracoords.txt, ensure you create a .txt file and update/include new name if different
                        file1 = open("cameracoords.txt", "a+")
                        x_coord = str(dist_x)
                        y_coord = str(dist_y)
                        L = [x_coord, y_coord]
                        
                        coordinate_string = ','.join(L)
                        file1.write(coordinate_string)

                        file1.write("\n")
                        file1.close()
                        
                        # Send coordinates from laptop to raspberrypi
                        #    .sendall(...) Sends encoded string over network connection sending ALL bytes.
                        #    coordinate_string formats and joins string correctly
                        #    .encode('utf-8') Convert string to bytes, needs to be done to send data over a network
                        connection.sendall(coordinate_string.encode('utf-8'))

                        # Overlay dist_x and dist_y on the frame
                        cv2.putText(frame, f"X: {dist_x}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(frame, f"Y: {dist_y}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('Frame', frame)
            k = cv2.waitKey(20)
            if k == 113:  # 'q' key to exit
                print("Connection to client closed")
                break
        else:
            break
    vid_capture.release()
    cv2.destroyAllWindows()