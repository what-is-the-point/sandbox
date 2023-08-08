########################################################
#   Title: AllSky Camera Thread
#  Thread: ascam Thread
# Project: UAP AllSky Detector
# Version: 0.0.1
#    Date: August 2023
#  Author: Carson Horne based on code from Zach Leffke, KJ4QLP and RkBlog at https://rk.edu.pl/en/scripting-machine-vision-and-astronomical-cameras-python/
# Comment:
########################################################




import argparse
import datetime
import imutils
import cv2
import numpy as np
import zwoasi as asi
import math
import threading
from queue import Queue
from daemon.logger import *



# # Initialize the ZWO Camera and video stream
class AllSky_Thread(threading.Thread):

    def __init__ (self, cfg, parent):
        threading.Thread.__init__(self)
        self._stop  = threading.Event()
        self.cfg    = cfg
        print(cfg)
        self.parent = parent
        self.thread_name = ".".join([self.cfg['name'],self.cfg['type']])
        self.setName(self.thread_name)
        self.logger = logging.getLogger(self.cfg['main_log'])

        self.rx_q  = Queue()
        self.tlm_q = Queue()
        self.ctl_q = Queue()
        self.tx_q = Queue()
        self.buffer = ''

        self.logger.info("Initializing {}".format(self.name))

        asi.init('/home/carson/github/ASI_linux_mac_SDK_V1.29/lib/x64/libASICamera2.so')
        self.num_cameras = asi.get_num_cameras()
        if self.num_cameras == 0:
            raise ValueError('No cameras found')

        self.camera_id = 0
        self.cameras_found = asi.list_cameras()
        print(self.cameras_found)
        self.camera = asi.Camera(self.camera_id)
        self.camera_info = self.camera.get_camera_property()
        print(self.camera_info)
        

        # Set default camera settings
        self.camera.disable_dark_subtract()
        #camera.set_control_value(asi.ASI_GAIN, 3)
        #camera.set_control_value(asi.ASI_EXPOSURE, 100) # microseconds
        self.camera.set_control_value(asi.ASI_WB_B, 90)
        self.camera.set_control_value(asi.ASI_WB_R, 60)
        self.camera.set_control_value(asi.ASI_GAMMA, 20)
        self.camera.set_control_value(asi.ASI_BRIGHTNESS, 5)
        self.camera.set_control_value(asi.ASI_FLIP, 0)
        #camera.set_roi_format(800,800,1,1)

        print('Enabling video mode')
        self.camera.auto_exposure()
        self.camera.auto_wb()

        self.camera.start_video_capture()

        self.camera.set_image_type(asi.ASI_IMG_RGB24)
        
    def run(self):
        self.logger.info('Launched {:s}'.format(self.name))
        # self._init_socket()
        while (not self._stop.isSet()):
        # grab the current frame and initialize the occupied/unoccupied
        # text
            self.frame = self.camera.capture_video_frame()
        # if the frame could not be grabbed, then we have reached the end
        # of the video
            if self.frame is None:
                break
        # convert frame to grayscale, and blur it
            self.frame = np.asarray(self.frame)
            self.tx_q.put(self.frame)
          

        # Stop the camera and close any open windows
    def stop(self):
        #self.conn.close()
        #cv2.destroyAllWindows()
        self.camera.stop_video_capture()
        self.camera.close()
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
        
