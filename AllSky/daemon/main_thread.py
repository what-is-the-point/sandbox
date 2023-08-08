########################################################
#   Title: Main Thread
#  Thread: Main Thread
# Project: UAP AllSky Detector
# Version: 0.0.1
#    Date: August 2023
#  Author: Carson Horne based on code from Zach Leffke, KJ4QLP
# Comment:
########################################################


import threading
import os
import math
import sys
import string
import time
import socket
import json
import binascii
import datetime
import uuid
import copy
from daemon.logger import *
from daemon.allsky_thread import *
from daemon.image_processing_thread import *
from daemon.sbs1_thread import *
from daemon.mlat_thread import *
from daemon.adsb_utilities import *
#from gui.generic_gui import *
# from daemon.Focus_Service import *

class Main_Thread(threading.Thread):
    """ docstring """
    def __init__ (self, cfg):
        threading.Thread.__init__(self, name = 'MainThread')
        self._stop      = threading.Event()
        self.cfg = cfg
        self.thread_enable = self.cfg['thread_enable']

        self.main_log_fh = setup_logger(self.cfg['main']['log'])
        self.logger = logging.getLogger(self.cfg['main']['log']['name']) #main logger
        self.logger.info("configs: {:s}".format(json.dumps(self.cfg)))

        self.state  = 'BOOT' #BOOT, IDLE, STANDBY, ACTIVE, FAULT, CALIBRATE
        self.state_map = {
            'BOOT':0x00,        #bootup
            'IDLE':0x01,        #threads launched, no connections, attempt md01 connect
            'STANDBY':0x02,     #user connected, md01 connected
            'ACTVE':0x04,       #clien activated system, launch az/el logger
            'CALIBRATE':0x08,   #calibration mode, future use
            'FAULT':0x80        #some kind of fault has occured
        }

        self.sbs1_tlm = None
        self.mlat_tlm = None
        self.frame = None

        self.sbs1_msg = None
        self.mlat_msg = None

        self.obs_lat = self.cfg['main']['observer']['lat']
        self.obs_lon = self.cfg['main']['observer']['lon']
        self.obs_alt = self.cfg['main']['observer']['alt']

        self.trk_msg = copy.deepcopy(track_msg)
        self.last_trk_msg = copy.deepcopy(track_msg)


    def run(self):
        print("Main Thread Started...")
        self.logger.info('Launched main thread')
        try:
            while (not self._stop.isSet()):
                if self.state == 'BOOT':
                    #starting up, Activate all threads
                    #State Change if all is well:  BOOT --> IDLE
                    if self._init_threads():#if all threads activate succesfully
                        self.logger.info('Successfully Launched Threads, Switching to IDLE State')
                        self._set_state('IDLE')
                        time.sleep(1)
                    #else:
                    #    self._set_state('FAULT')
                elif self.state == 'FAULT':
                    print("in FAULT state, exiting")
                    sys.exit()
                else:# NOT IN BOOT State


                    if (self.thread_enable['ascam'] and (not self.allsky_thread.tx_q.empty())):
                        msg = self.allsky_thread.tx_q.get()
                        self.frame = msg
                        self.image_processing_thread.rx_q.put(self.frame)
                    
                    """ if (self.thread_enable['opencv'] and (not self.image_processing_thread.tx_q.empty())):
                        msg = self.image_processing_thread.tx_q.get()
                        self.frame = msg
                        self.gui_thread.rx_q.put(self.frame) """

                    if (self.thread_enable['sbs1'] and (not self.sbs1_thread.tlm_q.empty())):
                        msg = self.sbs1_thread.tlm_q.get()
                        self.sbs1_tlm = msg
                        print(self.sbs1_tlm)

                    if (self.thread_enable['sbs1'] and (not self.sbs1_thread.tx_q.empty())):
                        adsb_msg = self.sbs1_thread.tx_q.get()
                        self.image_processing_thread.tlm_q.put(adsb_msg)
                        #print(adsb_msg)

                time.sleep(0.000001)

        except (KeyboardInterrupt): #when you press ctrl+c
            self.logger.warning('Caught CTRL-C, Terminating Threads...')
        except SystemExit:
            self.logger.warning('Terminated Main Thread...')
        self.logger.warning('Terminated Main Thread...')
        sys.exit()

    ###################################################################
    #                   STATE CONTROL FUNCTIONS
    ###################################################################

    def _do_idle(self):
        #print self.user_con, self.md01_con
        #if self.user_con and self.md01_con:
        #    self.logger.info("Connection Status (USER/MD01): ".format(self.user_con, self.md01_con))
        #    self._set_state('STANDBY')
        self._check_con_status()

    def _do_standby(self):
        #USER Connected
        #MD01 Connected
        self._check_con_status()
        pass

    def _do_active(self):
        if (self.thread_enable['cli'] and (not self.cli_thread.cmd_q.empty())):
            msg = self.cli_thread.cmd_q.get()
            self._process_cmd_message(msg)
      

    def _do_calibrate(self):
        pass

    def _set_state(self, state):
        self.state = state
        # if self.state in ['IDLE', 'STANDBY', 'FAULT']: self._stop_thread_logging()
        if self.state == 'ACTIVE':
            self.gui_thread.tx_q.queue.clear()
            self.gui_thread.rx_q.put(self.dev_tlm)
        



        self.logger.info('Changed STATE to: {:s}'.format(self.state))

    ###################################################################
    #                   END STATE CONTROL FUNCTIONS
    ###################################################################


    def _process_ctl_message(self, msg):
        '''Process CTL Message for daemon/thread control'''
        print(json.dumps(msg, indent=2))
        if msg['type']=="CTL":
            if msg['cmd']=='RESET':  self._reset()
            elif msg['cmd']=='EXIT':   self.__terminate__()
            elif msg['cmd']=='STATUS': self._get_status()


    def _update_observer_location(self,msg):
        self.obs_lat = msg['params']['lat']
        self.obs_lon = msg['params']['lon']
        self.obs_alt = msg['params']['alt']
        self.logger.debug("Updated Observer Location: {:3.6f}, {:2.6f}, {:f}".format(self.obs_lat,
                                                                                     self.obs_lon,
                                                                                     self.obs_alt))

    def _process_adsb_ctl_message(self,msg):
        # print(msg)

        if self.thread_enable['sbs1'] and ('ADSB' in msg['dest']):
            self.sbs1_thread.ctl_q.put(msg)
        if self.thread_enable['mlat'] and ('MLAT' in msg['dest']):
            self.mlat_thread.ctl_q.put(msg)

        if msg['cmd']=='select_icao':
            self.trk_msg = copy.deepcopy(track_msg)
            self.trk_msg['icao'] = msg['params']['icao']
        if msg['cmd']=='cancel_icao':
            self.trk_msg = copy.deepcopy(track_msg)






    def _process_mlat_ctl_message(self,msg):
        # print(msg)

        if self.thread_enable['sbs1'] and ('ADSB' in msg['dest']):
            self.sbs1_thread.ctl_q.put(msg)
        if self.thread_enable['mlat'] and ('MLAT' in msg['dest']):
            self.mlat_thread.ctl_q.put(msg)


        if msg['cmd']=='select_icao':
            self.trk_msg = copy.deepcopy(track_msg)
            self.trk_msg['icao'] = msg['params']['icao']
        if msg['cmd']=='cancel_icao':
            self.trk_msg = copy.deepcopy(track_msg)

    ###################################################################
    #                   Thread Control Functions
    ###################################################################
    def _get_status(self):
        self.logger.warning('Get Program Status called by CLI....to be implemented...')

    def _init_threads(self):
        try:
            #Initialize Threads
            self.logger.info("Thread enable: {:s}".format(json.dumps(self.thread_enable)))
            for key in self.thread_enable.keys():
                if self.thread_enable[key]:
                    if key == 'ascam': #Initialize Allsky Thread
                        self.logger.info('Setting up Allsky Thread')
                        self.allsky_thread = AllSky_Thread(self.cfg['ascam'], self) #PTU Thread
                        self.allsky_thread.daemon = True
                    elif key == 'opencv': #Initialize Image Processing Thread
                        self.logger.info('Setting up Image Processing Thread')
                        self.image_processing_thread = Image_Processing_Thread(self.cfg['opencv'], self) #PTU Thread
                        self.image_processing_thread.daemon = True
                    elif key == 'sbs1': #Initialize ADSB SBS1 Thread
                        self.logger.info('Setting up ADSB SBS1 Thread')
                        self.sbs1_thread = SBS1_Thread(self.cfg['sbs1'], self) #ADSB SBS1 Thread
                        self.sbs1_thread.daemon = True
                    """ elif key == 'mlat': #Initialize ADSB SBS1 Thread
                        self.logger.info('Setting up MLAT SBS1 Thread')
                        self.mlat_thread = MLAT_Thread(self.cfg['mlat'], self) #MLAT SBS1 Thread
                        self.mlat_thread.daemon = True """

            #Launch threads
            for key in self.thread_enable.keys():
                if self.thread_enable[key]:
                    if key == 'ascam': #Initialize Allsky Thread
                        self.logger.info('Launching Allsky Thread')
                        self.allsky_thread.start() #non-blocking
                    elif key == 'opencv': #Initialize Image Processing Thread
                        self.logger.info('Launching Image Processing Thread')
                        self.image_processing_thread.start() #non-blocking
                    elif key == 'sbs1': #Start Service Thread
                        self.logger.info('Launching ADSB SBS1 Thread')
                        self.sbs1_thread.start() #non-blocking
                    """ elif key == 'mlat': #Start Service Thread
                        self.logger.info('Launching MLAT SBS1 Thread')
                        self.mlat_thread.start() #non-blocking """
            return True
        except Exception as e:
            self.logger.error('Error Launching Threads:', exc_info=True)
            self.logger.warning('Setting STATE --> FAULT')
            self._set_state('FAULT')
            return False

    def _stop_threads(self):
        for key in self.thread_enable.keys():
            if self.thread_enable[key]:
                if key == 'ascam': #Terminate Allsky Thread
                    self.allsky_thread.stop()
                    self.logger.warning("Terminated Allsky Thread.")
                elif key == 'opencv': #Terminate Image Processing Thread
                    self.image_processing_thread.stop()
                    self.logger.warning("Terminated Image Processing Thread.")
                elif key == 'sbs1':
                    self.sbs1_thread.stop()
                    self.logger.warning("Terminated ADSB SBS1 Thread.")
                """ elif key == 'mlat':
                    self.mlat_thread.stop()
                    self.logger.warning("Terminated MLAT SBS1 Thread.") """

    def get_state(self):
        return self.state

    def set_gui_callback(self, cb):
        self.gui_thread = cb
    #---END STATE FUNCTIONS----

    def __terminate__(self):
        self.logger.warning('Terminating Threads...')
        self._stop_threads()
        self.logger.warning('Terminating Main Thread...')
        self.stop()


    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
