########################################################
#   Title: Image Processing Thread
#  Thread: OpenCV Thread
# Project: UAP AllSky Detector
# Version: 0.0.1
#    Date: August 2023
#  Author: Carson Horne based on code from Zach Leffke, KJ4QLP
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

class Image_Processing_Thread(threading.Thread):
    
    def __init__ (self, cfg, parent):
        threading.Thread.__init__(self)
        self._stop  = threading.Event()
        self.cfg    = cfg
        print(cfg)
        self.parent = parent
        self.thread_name = ".".join([self.cfg['name'],self.cfg['type']])
        self.setName(self.thread_name)
        self.logger = logging.getLogger(self.cfg['main_log'])
        self.dict={}
        self.rx_q  = Queue()
        self.tlm_q = Queue()
        self.ctl_q = Queue()
        self.tx_q = Queue()
        self.buffer = ''

        self.logger.info("Initializing {}".format(self.name))

    def run(self):
        self.logger.info('Launched {:s}'.format(self.name))
        
        while (not self._stop.isSet()):
            # grab the current frame and initialize the occupied/unoccupied
            # text
            self.frame = self.rx_q.get()
            if not self.tlm_q.empty():
                self.dict = self.tlm_q.get()
                for key in self.dict:
                    r=19.55*(90-self.dict[key][1])
                    PixX = int(1969+r*math.cos((360-self.dict[key][0])*math.pi/180-math.pi/2))
                    PixY = int(1080+r*math.sin((360-self.dict[key][0])*math.pi/180-math.pi/2))
                    cv2.circle(self.frame, (PixX,PixY), 20, (0,0,255),3)
                    cv2.putText(self.frame, key,((PixX+23),PixY),cv2.FONT_HERSHEY_SIMPLEX, 1.35, (0, 0, 255), 4)
            
            else:
                for key in self.dict:
                    r=19.55*(90-self.dict[key][1])
                    PixX = int(1969+r*math.cos((360-self.dict[key][0])*math.pi/180-math.pi/2))
                    PixY = int(1080+r*math.sin((360-self.dict[key][0])*math.pi/180-math.pi/2))
                    cv2.circle(self.frame, (PixX,PixY), 20, (0,0,255),3)
                    cv2.putText(self.frame, key,((PixX+23),PixY),cv2.FONT_HERSHEY_SIMPLEX, 1.35, (0, 0, 255), 4)
            
            cv2.circle(self.frame, (1969,1080), 1662, (0,255,0),2)
            cv2.circle(self.frame, (1969,1080), int((10*19.55)), (0,255,0),2)
            cv2.circle(self.frame, (1969,1080), int((20*19.55)), (0,255,0),2)
            cv2.circle(self.frame, (1969,1080), int((30*19.55)), (0,255,0),2)
            cv2.circle(self.frame, (1969,1080), int((40*19.55)), (0,255,0),2)
            cv2.circle(self.frame, (1969,1080), int((50*19.55)), (0,255,0),2)
            cv2.circle(self.frame, (1969,1080), int((60*19.55)), (0,255,0),2)
            cv2.circle(self.frame, (1969,1080), int((70*19.55)), (0,255,0),2)
            cv2.circle(self.frame, (1969,1080), int((80*19.55)), (0,255,0),2)
            cv2.line(self.frame, (1969,0),(1969,2160),(0,255,0),2)
            cv2.line(self.frame, (0,1080),(3840,1080),(0,255,0),2)
            cv2.putText(self.frame, "N",(1954,40),cv2.FONT_HERSHEY_SIMPLEX, 1.35, (0, 0, 255), 4)
            cv2.putText(self.frame, "S",(1954,2154),cv2.FONT_HERSHEY_SIMPLEX, 1.35, (0, 0, 255), 4)
            cv2.putText(self.frame, "E",(304,1080),cv2.FONT_HERSHEY_SIMPLEX, 1.35, (0, 0, 255), 4)
            cv2.putText(self.frame, "W",(3622,1080),cv2.FONT_HERSHEY_SIMPLEX, 1.35, (0, 0, 255), 4)
            cv2.putText(self.frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),(10, self.frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.35, (0, 0, 255), 2)
            # show the frame and record if the user presses a key
            cv2.namedWindow("AllSky Feed", cv2.WINDOW_NORMAL)
            cv2.imshow("AllSky Feed", self.frame)
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key is pressed, break from the loop
            if key == ord("q"):
                break

            # Stop the camera and close any open windows
    def stop(self):
        #self.conn.close()
        cv2.destroyAllWindows()
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()