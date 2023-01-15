#!/usr/bin/env python3
#################################################
#   Title: Device Thread for Nexstar Controller
# Project: What's The Point
# Version: 0.0.1
#    Date: Jan, 2023
#  Author: Zach Leffke, KJ4QLP
# Comment:
#################################################

import math
import string
import time
import sys
import os
import threading
import json
import struct
import binascii
import numpy as np
import copy
import serial
import nexstar

from queue import Queue
from daemon.logger import *
from daemon.Autostar import *


class Device_Thread(threading.Thread):
    def __init__(self, cfg, parent = None):
        threading.Thread.__init__(self, name=cfg['name'])
        self._stop  = threading.Event()
        self.cfg    = cfg
        self.parent = parent
        self._init_thread()

    def _init_thread(self):
        self.logger = logging.getLogger(self.cfg['main_log'])
        self.logger.info("Initializing {:s} Device Thread for {:s} Protocol".format(self.cfg['type'],
                                                                           self.cfg['protocol']))
        self.tx_q = Queue() # Main_Thread -> Device
        self.rx_q = Queue() # Main_thread <- Device
        self.port    = self.cfg['connection']['port']
        self.connected = False
        self.observer = self.cfg['observer']
        self.tlm = { #Thread control Telemetry message
            "type":"TLM", #Message Type: Thread Telemetry
            "src": "device",
            "connected":False, #Socket Connection Status
        }

        self.nexstar = {
            "type": 'RX',
            'src':'device',
            "cur_az": 0.0,
            "cur_el": 0.0,
            "tar_az": 0.0,
            "tar_el": 0.0,
            "gtip": False,
            "model": "",
            "version": "",
            "mode":""
        }


    def run(self):
        '''
        Main Run Loop
        -check socket connection for feedback
        -send commands to PTU over socket
        '''
        self.logger.info("{:s} Started".format(self.name))
        while (not self._stop.isSet()):
            if not self.tx_q.empty(): #Received Message from Main Thread
                msg = self.tx_q.get() #retrieve message from FIFO buffer
                self._process_command(msg)
            time.sleep(0.001)
            pass

    def _process_command(self, msg):
        """ Received Command From Main Thread for Serial Port """
        self.logger.info("Received Device Command Plane Message: {:s}".format(json.dumps(msg)))
        if msg['type']=="connect": self._handle_connection(msg)
        else:
            if self.connected: self._process_device_command(msg)


    #####################################################################
    #### Serial Port Connection Functions ###############################
    #####################################################################

    def _process_device_command(self, msg):
        print(msg)
        try:
            if "position" in msg['type']:
                self.nexstar['cur_az'], self.nexstar['cur_el'] = self.ns.getPosition()
                self.nexstar['gtip'] = self.ns.getGotoInProgress()
            elif 'goto' in msg['type']:
                self.nexstar['tar_az']=msg['params']['azimuth']
                self.nexstar['tar_el']=msg['params']['elevation']
                self.ns.gotoPosition(msg['params']['azimuth'],
                                     msg['params']['elevation'])
            elif 'slew' in msg['type']:
                self.ns.slew_fixed(nexstar.NexstarDeviceId.AZM_RA_MOTOR,msg['params']['az_val'])
                self.ns.slew_fixed(nexstar.NexstarDeviceId.ALT_DEC_MOTOR,msg['params']['el_val'])
            elif msg['type']=='stop':
                self.ns.cancelGoto()
            elif msg['type'] == 'focus_speed':
                self.send_msg(self.encoder.encode_focus_speed(msg['params']['speed']))
            elif msg['type'] == 'focus_in':
                self.send_msg(self.encoder.encode_focus_inward())
            elif msg['type'] == 'focus_out':
                self.send_msg(self.encoder.encode_focus_outward())
            elif msg['type'] == 'focus_stop':
                self.send_msg(self.encoder.encode_focus_stop())
        except nexstar.NexstarProtocolError as e:
            self.logger.debug("Nexstar Protocol Error")
            self.logger.debug(e)
            self._disconnect()
        except Exception as e:
            self.logger.info(sys.exc_info())
            pass
        print(self.nexstar)
        self.rx_q.put(self.nexstar)




    def _connect(self,msg=None):
        try:
            self.ns = nexstar.NexstarHandController(self.port)
            time.sleep(0.05)
            self.nexstar['model']=self._parse_model(self.ns.getModel())
            print(self.nexstar['model'])
            self.logger.info("Opened Nexstar Serial Port: {:s}".format(self.port))
            self.connected = True

        except Exception as e:
            self.logger.debug("Problem Opening Serial Port: {:s}".format(self.port))
            self.logger.debug(e)
            self.connected = False

        self.tlm = { #Thread control Telemetry message
            "type":"TLM", #Message Type: Thread Telemetry
            "src": "device",
            "connected":False, #Socket Connection Status
        }
        self.tlm['connected']=self.connected
        self.tx_q.queue.clear()
        self.rx_q.queue.clear()
        self.rx_q.put(self.tlm)
        if self.connected: self._init_nexstar()

    def _init_nexstar(self):
        self.logger.info("Setting Location: {:f},{:f}".format(self.observer['lat'],
                                                              self.observer['lon']))
        self.ns.setLocation(self.observer['lat'], self.observer['lon'])
        self.nexstar['gtip'] = self.ns.getGotoInProgress()
        self.nexstar['cur_az'], self.nexstar['cur_el'] = self.ns.getPosition()
        self.rx_q.put(self.nexstar)
        nexstar.status_report(self.ns)


    def _disconnect(self):
        self.ns.close()
        self.logger.info("Closed Nexstar Serial Port: {:s}".format(self.port))
        self.connected = False
        self.tlm['connected']=self.connected
        self.rx_q.put(self.tlm)

    def _handle_connection(self, msg):
        if msg['params']['connect']: #Start Serial Connection
            self._connect(msg)
        else: #Stop Serial Cpnnection
            self._disconnect()

    def _parse_model(self,model):
        if model == 1:
            return "gps_series"
        elif model == 3:
            return "i_series"
        elif model == 4:
            return "i_series_se"
        elif model == 5:
            return "cge"
        elif model == 6:
            return "advanced_gt"
        elif model == 7:
            return "slt"
        elif model == 9:
            return "cpc"
        elif model == 10:
            return "gt"
        elif model == 11:
            return "se45"
        elif model == 12:
            return "se68"
        elif model == 15:
            return "lcm"
        else:
            return 'unknown'

    #### Class Thread Handler ###########
    def get_tlm(self):
        ''' Called by Main Thread '''
        return self.tlm

    def stop(self):
        #self.conn.close()
        if self.connected: self._disconnect()
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
