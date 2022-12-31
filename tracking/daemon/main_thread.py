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
from daemon.sbs1_thread import *
from daemon.adsb_utilities import *
from gui.generic_gui import *
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

        self.dev_tlm = None
        self.sbs1_tlm = None
        self.mlat_tlm = None

        self.sbs1_msg = None
        self.mlat_msg = None

        self.obs_lat = self.cfg['main']['observer']['lat']
        self.obs_lon = self.cfg['main']['observer']['lon']
        self.obs_alt = self.cfg['main']['observer']['alt']

        self.trk_msg = track_msg


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
                    if (self.thread_enable['cli'] and (not self.cli_thread.ctl_q.empty())):
                        msg = self.cli_thread.ctl_q.get()
                        self._process_ctl_message(msg)

                    if (self.thread_enable['gui'] and (not self.gui_thread.tx_q.empty())):
                        msg = self.gui_thread.tx_q.get()
                        self._process_gui_message(msg)

                    if (self.thread_enable['sbs1'] and (not self.sbs1_thread.tlm_q.empty())):
                        msg = self.sbs1_thread.tlm_q.get()
                        self.sbs1_tlm = msg
                        self.gui_thread.rx_q.put(self.sbs1_tlm)

                    if (self.thread_enable['mlat'] and (not self.mlat_thread.tlm_q.empty())):
                        msg = self.mlat_thread.tlm_q.get()
                        self.mlat_tlm = msg
                        self.gui_thread.rx_q.put(self.mlat_tlm)

                    if (self.thread_enable['sbs1'] and (not self.sbs1_thread.rx_q.empty())):
                        msg = self.sbs1_thread.rx_q.get()
                        self._do_auto_track(msg)

                    if (self.thread_enable['mlat'] and (not self.mlat_thread.rx_q.empty())):
                        msg = self.mlat_thread.rx_q.get()
                        self._do_auto_track(msg)

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
        if (self.thread_enable['cli'] and (not self.cli_thread.cmd_q.empty())):
            msg = self.cli_thread.cmd_q.get()
            self._process_cmd_message(msg)
        self._check_con_status()

        if (self.thread_enable['dev'] and (not self.device_thread.rx_q.empty())):
            msg = self.device_thread.rx_q.get()
            self._process_dev_message(msg)



        # self.dev_stat = self.device_thread.get_status()
        # self.gui_thread.rx_q.put(self.dev_stat)

    def _do_calibrate(self):
        pass

    def _set_state(self, state):
        self.state = state
        # if self.state in ['IDLE', 'STANDBY', 'FAULT']: self._stop_thread_logging()
        if self.state == 'ACTIVE':
            # self.cli_thread.cmd_q.queue.clear()
            self.gui_thread.tx_q.queue.clear()
            self.gui_thread.rx_q.put(self.dev_tlm)
        #     ts = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        #     session_id = uuid.uuid4()
        #     #print self._utc_ts() + "Started Session ID: {:s}".format(self.session_id)
        #     self.logger.info("Started Session ID: {:s}".format(self.session_id))
        #     self._start_thread_logging(ts, ssid)
        #     self._send_session_start()

        if self.state =='IDLE':
            if self.dev_tlm:
                self.gui_thread.rx_q.put(self.dev_tlm)

        self.logger.info('Changed STATE to: {:s}'.format(self.state))

    ###################################################################
    #                   END STATE CONTROL FUNCTIONS
    ###################################################################

    def _do_auto_track(self, msg):
        # print(msg)
        try:
            if msg['msg_type'] == 'MSG':
                self.trk_msg['msg_src'] = 'ADSB'
                self.trk_msg['icao'] = msg['hex_ident']

                time_str = "{:s} {:s}".format(msg['generated_date'], msg['generated_time'])
                timestamp = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S.%f")
                timestamp = timestamp+datetime.timedelta(seconds=18000)
                now_ts = datetime.datetime.utcnow()
                delta_t = (now_ts - timestamp).total_seconds() #convert to UTC from Eastern
                self.trk_msg['age']=delta_t
                self.trk_msg['date_last'] = timestamp.strftime("%Y-%m-%d")
                self.trk_msg['time_last'] = timestamp.strftime("%H:%M:%S.%fZ")
                self.trk_msg['msg_cnt'] += 1

                if msg['tx_type'] == 1:
                    self.trk_msg['callsign'] = msg['callsign']
                elif msg['tx_type'] == 3: #Extended Squitter Airborne Position Message
                    self.trk_msg['latitude'] = msg['latitude']
                    self.trk_msg['longitude'] = msg['longitude']
                    self.trk_msg['geo_alt'] = msg['altitude']
                    try:
                        razel = RAZEL(self.obs_lat, self.obs_lon, self.obs_alt / 1000.0,
                                      msg['latitude'], msg['longitude'], msg['altitude']*0.0003048)
                        self.trk_msg['range']     = razel['rho']
                        self.trk_msg['azimuth']   = razel['az']
                        self.trk_msg['elevation'] = razel['el']
                    except Exception as e:
                        self.logger.debug("Error in RAZEL Function: {:s}".format(str(e)))
                elif msg['tx_type'] == 4: #Extended Squitter Airborne Velocity Message
                    self.trk_msg['speed'] = msg['ground_speed']
                    self.trk_msg['track'] = msg['track']
                    self.trk_msg['vert_rate'] = msg['vertical_rate']
                elif msg['tx_type'] == 5: #Surveillance altitude Message, triggered by radar
                    self.trk_msg['baro_alt'] = msg['altitude']

            track_msg = {}
            track_msg['src'] = 'track'
            track_msg['msg'] = copy.deepcopy(self.trk_msg)
            self.gui_thread.rx_q.put(track_msg)
        except Exception as e:
            self.logger.debug("Error in AutoTrack Function: {:s}".format(str(e)))





    def _check_con_status(self):
        '''
        Checks ADSB Receiver and RabbitMQ broker connection status
        sets Daemon state accordingly
        '''
        if (self.thread_enable['dev']):
            self.dev_tlm = self.device_thread.get_tlm()

            if self.dev_tlm['connected']:
                if self.state=='IDLE': self._set_state('ACTIVE')

            if not self.dev_tlm['connected']:
                if self.state =='ACTIVE': self._set_state('IDLE')

    def _process_gui_message(self, msg):
        '''Process GUI Message for daemon/thread control'''
        print(json.dumps(msg, indent=2))
        if 'type' in msg.keys():
            if msg['type']=='CTL':
                if msg['cmd']=='EXIT': self.__terminate__()
                elif msg['cmd']=='location': self._update_observer_location(msg)
                elif msg['dest']=='ADSB': self._process_adsb_ctl_message(msg)

        else:
            self.device_thread.tx_q.put(msg['body'])

    def _process_ctl_message(self, msg):
        '''Process CTL Message for daemon/thread control'''
        print(json.dumps(msg, indent=2))
        if msg['type']=="CTL":
            if msg['cmd']=='RESET':  self._reset()
            elif msg['cmd']=='EXIT':   self.__terminate__()
            elif msg['cmd']=='STATUS': self._get_status()

    def _process_cmd_message(self, msg):
        '''Process CMD Message for device control'''
        # print(json.dumps(msg, indent=2))
        self.device_thread.tx_q.put(msg['body'])

    def _process_dev_message(self, msg):
        if msg['type']=='RX':
            self.gui_thread.rx_q.put(msg)

    def _update_observer_location(self,msg):
        self.obs_lat = msg['params']['lat']
        self.obs_lon = msg['params']['lon']
        self.obs_alt = msg['params']['alt']
        self.logger.debug("Updated Observer Location: {:3.6f}, {:2.6f}, {:f}".format(self.obs_lat,
                                                                                     self.obs_lon,
                                                                                     self.obs_alt))

    def _process_adsb_ctl_message(self,msg):
        print(msg)
        if self.thread_enable['sbs1'] and msg['dest']=='ADSB':
            self.sbs1_thread.ctl_q.put(msg)
        if self.thread_enable['mlat'] and msg['dest']=='MLAT':
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
                    if key == 'dev': #Initialize Device Thread
                        self.logger.info('Setting up Device Thread')
                        self.device_thread = Device_Thread(self.cfg['dev'], self) #PTU Thread
                        self.device_thread.daemon = True
                    elif key == 'cli': #Initialize Device Thread
                        self.logger.info('Setting up CLI Thread')
                        self.cli_thread = Simple_CLI(self.cfg['cli'], self) #PTU Thread
                        self.cli_thread.daemon = True
                    elif key == 'sbs1': #Initialize ADSB SBS1 Thread
                        self.logger.info('Setting up ADSB SBS1 Thread')
                        self.sbs1_thread = SBS1_Thread(self.cfg['sbs1'], self) #ADSB SBS1 Thread
                        self.sbs1_thread.daemon = True
                    elif key == 'mlat': #Initialize ADSB SBS1 Thread
                        self.logger.info('Setting up MLAT SBS1 Thread')
                        self.mlat_thread = MLAT_Thread(self.cfg['mlat'], self) #MLAT SBS1 Thread
                        self.mlat_thread.daemon = True

            #Launch threads
            for key in self.thread_enable.keys():
                if self.thread_enable[key]:
                    if key == 'dev': #Initialize Device Thread
                        self.logger.info('Launching Device Thread')
                        self.device_thread.start() #non-blocking
                    elif key == 'cli': #Initialize CLI Thread
                        self.logger.info('Launching CLI Thread')
                        self.cli_thread.start() #non-blocking
                    elif key == 'sbs1': #Start Service Thread
                        self.logger.info('Launching ADSB SBS1 Thread')
                        self.sbs1_thread.start() #non-blocking
                    elif key == 'mlat': #Start Service Thread
                        self.logger.info('Launching MLAT SBS1 Thread')
                        self.mlat_thread.start() #non-blocking
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
                elif key == 'sbs1':
                    self.sbs1_thread.stop()
                    self.logger.warning("Terminated ADSB SBS1 Thread.")
                elif key == 'mlat':
                    self.mlat_thread.stop()
                    self.logger.warning("Terminated MLAT SBS1 Thread.")

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
