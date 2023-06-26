#initial base for ZWO camera operation came from RkBlog at https://rk.edu.pl/en/scripting-machine-vision-and-astronomical-cameras-python/
#initial base for TCP socket communication came from https://adyraj.medium.com/video-streaming-using-python-ed73dc5bcb30

import argparse
import socket
import pickle
import datetime
import imutils
import cv2
import numpy as np
import zwoasi as asi
import struct


# # construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--min-area", type=int, default=10, help="minimum area size")
args = vars(ap.parse_args())

# # Initialize the ZWO Camera and video stream
asi.init('/home/ubuntu/ASI_linux_mac_SDK_V1.29/lib/armv8/libASICamera2.so')  #Currently configured for a Raspberry Pi4 to serve as the imaging capture computer.  A standard computing device will require the x64 SDK file.

num_cameras = asi.get_num_cameras()
if num_cameras == 0:
    raise ValueError('No cameras found')

camera_id = 0
cameras_found = asi.list_cameras()
print(cameras_found)
camera = asi.Camera(camera_id)
camera_info = camera.get_camera_property()
print(camera_info)

# Set default camera settings
camera.disable_dark_subtract()
camera.set_control_value(asi.ASI_GAIN, 0)
camera.set_control_value(asi.ASI_EXPOSURE, 100) # microseconds
camera.set_control_value(asi.ASI_WB_B, 99)
camera.set_control_value(asi.ASI_WB_R, 75)
camera.set_control_value(asi.ASI_GAMMA, 50)
camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
camera.set_control_value(asi.ASI_FLIP, 0)
camera.set_roi(0,0,1920,1080, 2, 1)

print('Enabling video mode')
camera.auto_exposure()
camera.auto_wb()
camera.start_video_capture()
camera.set_image_type(asi.ASI_IMG_RGB24)


# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = '192.168.2.60' #Insert IP of image capture camera
print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)

# Socket Accept
while True:
	client_socket,addr = server_socket.accept()
	print('GOT CONNECTION FROM:',addr)
	#frame1 = camera.capture_video_frame()
	if client_socket:
		vid = True #cv2.VideoCapture(0)
		
		while(vid==True):
			frame = camera.capture_video_frame()#vid.read()
			cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.35, (0, 0, 255), 2)
			#frame = imutils.resize(frame,width=1920)
			a = pickle.dumps(frame)
			message = struct.pack("Q",len(a))+a
			client_socket.sendall(message)
			
			#cv2.imshow('TRANSMITTING VIDEO',frame)
			if cv2.waitKey(1) == 'q':
				client_socket.close()


