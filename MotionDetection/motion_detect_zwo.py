#initial base for ZWO camera operation came from RkBlog at https://rk.edu.pl/en/scripting-machine-vision-and-astronomical-cameras-python/
#initial base for OpenCV motion detection came from https://pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/


import argparse
import datetime
import imutils
import cv2
import numpy as np
import zwoasi as asi


# # construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--min-area", type=int, default=20, help="minimum area size")
args = vars(ap.parse_args())

# # Initialize the ZWO Camera and video stream
asi.init('/home/ubuntu/ASI_linux_mac_SDK_V1.28/lib/x64/libASICamera2.so')

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
camera.set_control_value(asi.ASI_GAIN, 75)
camera.set_control_value(asi.ASI_EXPOSURE, 100000) # microseconds
camera.set_control_value(asi.ASI_WB_B, 99)
camera.set_control_value(asi.ASI_WB_R, 75)
camera.set_control_value(asi.ASI_GAMMA, 50)
camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
camera.set_control_value(asi.ASI_FLIP, 0)
#camera.set_roi_format(800,800,1,1)

print('Enabling video mode')
camera.start_video_capture()
camera.set_image_type(asi.ASI_IMG_RGB24)

# # Begin OpenCV motion detection from video feed
firstFrame = None
# loop over the frames of the video
while True:
	# grab the current frame and initialize the occupied/unoccupied
	# text
	frame = camera.capture_video_frame()
   	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if frame is None:
		break
	# convert frame to grayscale, and blur it
	frame = np.asarray(frame)
	gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray
		continue
    # compute the absolute difference between the current frame and first frame
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
	# dilate the thresholded image to fill in holes, then find contours on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue
		# compute the bounding box for the contour, draw it on the frame
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
   	# draw the text and timestamp on the frame
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	# show the frame and record if the user presses a key
	cv2.namedWindow("AllSky Feed", cv2.WINDOW_NORMAL)
	#im = cv2.resize(frame, (960, 540))
	cv2.imshow("AllSky Feed", frame)
	#cv2.imshow("Thresh", thresh)
	#cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF
	# if the `q` key is pressed, break from the loop
	if key == ord("q"):
		break
# Stop the camera and close any open windows
cv2.destroyAllWindows()
camera.stop_video_capture()
camera.close()
