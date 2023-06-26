#This code came almost entirely from https://adyraj.medium.com/video-streaming-using-python-ed73dc5bcb30 and has only very minor modifications to increase transfer speeds

import socket
import cv2
import pickle
import struct


# create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '192.168.2.60' # paste your server ip address here
port = 9999
client_socket.connect((host_ip,port)) 
data = b""
payload_size = struct.calcsize("Q")
while True:
	while len(data) < payload_size:
		packet = client_socket.recv(30*1024) 
		if not packet: break
		data+=packet
	packed_msg_size = data[:payload_size]
	data = data[payload_size:]
	msg_size = struct.unpack("Q",packed_msg_size)[0]
	
	while len(data) < msg_size:
		data += client_socket.recv(30*1024)
	frame_data = data[:msg_size]
	data  = data[msg_size:]
	frame = pickle.loads(frame_data)
	cv2.namedWindow("RECEIVING VIDEO",cv2.WINDOW_NORMAL)
	cv2.imshow("RECEIVING VIDEO",frame)
	if cv2.waitKey(1) == 'q':
		break
client_socket.close()