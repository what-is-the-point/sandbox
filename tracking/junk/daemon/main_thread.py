#!/usr/bin/env python3
###############################################################
#   Title: Tracking Daemon Main Thread
# Project: WITP, ETX Telescope
# Version: 1.0.0
#    Date: Dec 17, 2022
#  Author: Zach Leffke, KJ4QLP
# Comment:
#  - Main Thread for tracking daemon
#  - Handles State Machine
#  - Flows communication between threads via python queues
###############################################################

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
from daemon.device_thread import *
from daemon.cli_thread import *
# from daemon.Focus_Service import *

class Main_Thread(threading.Thread):
    """ docstring """
    def __init__ (self, cfg):
        threading.Thread.__init__(self, name = 'Main   ')
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
                    # if (self.thread_enable['dev'] and (not self.device_thread.rx_q.empty())):
                    #     msg = self.device_thread.rx_q.get()
                    #     self._process_device_telemetry(msg)
                    if (self.thread_enable['cli'] and (not self.cli_thread.cmd_q.empty())):
                        msg = self.cli_thread.cmd_q.get()
                        self._process_c2_message(msg)

                    if self.state == 'IDLE':
                        self._do_idle() #wait for user conn AND mdo1 conn

                    elif self.state == 'STANDBY':
                        self._do_standby()

                    elif self.state == 'ACTIVE':
                        self._do_active()

                    elif self.state == 'CALIBRATE':
                        self._do_calibrate()

                time.sleep(0.001)

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

        pass

    def _do_calibrate(self):
        pass

    def _set_state(self, state):
        self.state = state
        # if self.state in ['IDLE', 'STANDBY', 'FAULT']: self._stop_thread_logging()
        if self.state == 'ACTIVE':
            ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            session_id = uuid.uuid4()
            #print self._utc_ts() + "Started Session ID: {:s}".format(self.session_id)
            self.logger.info("Started Session ID: {:s}".format(self.session_id))
            self._start_thread_logging(ts, ssid)
            self._send_session_start()

        self.logger.info('Changed STATE to: {:s}'.format(self.state))

    ###################################################################
    #                   END STATE CONTROL FUNCTIONS
    ###################################################################

    def _check_con_status(self):
        '''
        Checks ADSB Receiver and RabbitMQ broker connection status
        sets Daemon state accordingly
        '''
        if (self.thread_enable['dev']): self.dev_tlm = self.device_thread.get_tlm()


    def _process_c2_message(self, msg):
        print(json.dumps(msg, indent=2))
        if ((msg['type']=="CMD") and (msg['cmd']=="SEND")):
            # print(msg)
            # self._send_msg(msg['msg'])
            pass
        elif msg['type']=="CTL":
            if msg['cmd']=='RESET': self._reset()
            if msg['cmd']=='EXIT': self.__terminate__()




    ###################################################################
    #                   Thread Control Functions
    ###################################################################
    def _init_threads(self):
        try:
            #Initialize Threads
            self.logger.info("Thread enable: {:s}".format(json.dumps(self.thread_enable)))
            for key in self.thread_enable.keys():
                if self.thread_enable[key]:
                    if key == 'dev': #Initialize Device Thread
                        self.logger.info('Setting up Device Thread')
                        self.device_thread = Device_Thread(self.cfg['dev'], self) #PTU Thread
                        self.device_thread.daemon = True
                    elif key == 'cli': #Initialize Device Thread
                        self.logger.info('Setting up CLI Thread')
                        self.cli_thread = Simple_CLI(self.cfg['cli'], self) #PTU Thread
                        self.cli_thread.daemon = True

            #Launch threads
            for key in self.thread_enable.keys():
                if self.thread_enable[key]:
                    if key == 'dev': #Initialize Device Thread
                        self.logger.info('Launching Device Thread')
                        self.device_thread.start() #non-blocking
                    elif key == 'cli': #Initialize CLI Thread
                        self.logger.info('Launching CLI Thread')
                        self.cli_thread.start() #non-blocking
            return True
        except Exception as e:
            self.logger.error('Error Launching Threads:', exc_info=True)
            self.logger.warning('Setting STATE --> FAULT')
            self._set_state('FAULT')
            return False

    def _stop_threads(self):
        for key in self.thread_enable.keys():
            if self.thread_enable[key]:
                if key == 'dev': #Terminate Device Thread
                    self.device_thread.stop()
                    self.logger.warning("Terminated Device Thread.")
                elif key == 'cli': #Terminate CLI Thread
                    self.cli_thread.stop()
                    self.logger.warning("Terminated CLI Thread.")




    def get_state(self):
        return self.state
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
