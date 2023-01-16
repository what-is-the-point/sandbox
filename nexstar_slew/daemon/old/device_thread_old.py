#!/usr/bin/env python3
#################################################
#   Title: Moog QPT-500 Tracker Class
# Project: Multiple (VTGS)
# Version: 0.0.1
#    Date: August, 2022
#  Author: Zach Leffke, KJ4QLP
# Comment:
# - Tracker Class for controlling Moog QPT-500 Tracker
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
        if self.cfg['protocol'] == 'autostar':
            self.encoder = Autostar()
        elif self.cfg['protocol'] == 'nexstar':
            self.ns = nexstar.NexstarHandController(self.port)

        self.tlm = { #Thread control Telemetry message
            "type":"TLM", #Message Type: Thread Telemetry
            "src": "device",
            "connected":False, #Socket Connection Status
            "rx_count":0, #Number of received messages from device
            "tx_count":0, #Number of transmitted messages to device
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
    def _handle_connection(self, msg):
        if msg['params']['connect']: #Start Serial Connection
            self.port = msg['params']['port']
            self._open_serial()
        else: #Stop Serial Cpnnection
            self._close_serial()

    def _open_serial(self):
        self.conn = serial.Serial(port = self.port,
                                  baudrate = self.baud,
                                  timeout = self.timeout)
        # self.conn = serial.Serial(port = self.port,
        #                           baudrate = self.baud)
        self.logger.info("Opened Serial Port: [{:s} : {:d}]".format(self.port, self.baud))
        self._ser_fault = False
        self.connected = True
        self.tlm = { #Thread control Telemetry message
            "type":"TLM", #Message Type: Thread Telemetry
            "src": "device",
            "connected":False, #Socket Connection Status
            "rx_count":0, #Number of received messages from device
            "tx_count":0, #Number of transmitted messages to device
        }
        self.tlm['connected']=self.connected
        self.tx_q.queue.clear()
        self.rx_q.queue.clear()
        self.rx_q.put(self.tlm)

    def _close_serial(self):
        self.conn.close()
        self.connected = False
        self.tlm['connected']=self.connected
        self.rx_q.put(self.tlm)


    def send_msg(self,msg):
        self.logger.info("TX: {:s}: {:s}".format(msg['name'], msg['cmd']))
        self.conn.reset_output_buffer() #flush buffer
        try:
            self.conn.write(bytes(msg['cmd'], 'ascii'))
            self.tlm['tx_count'] += 1
        except Exception as e:
            self.logger.debug(sys.exc_info())

        if msg['resp'] != None:
            time.sleep(0.05)
            # print(len(msg['resp']), msg['resp'])
            data = self.conn.read(size=len(msg['resp']))
            if len(data)>0:
                # print(len(data), data)
                msg['resp'] = data.hex()
                self.logger.info("RX: {:s}".format(msg['resp']))
                self.tlm['rx_count'] += 1
                self.encoder.decode(msg)
                self.conn.reset_input_buffer() #flush buffer
            else:
                self.logger.debug("Serial port timeout, is the mount on?")
                self.conn.reset_input_buffer() #flush buffer

    def _process_device_command(self, msg):
        try:
            if "position" in msg['type']:
                self.send_msg(self.encoder.encode_get_azimuth())
                time.sleep(0.1)
                self.send_msg(self.encoder.encode_get_elevation())
            elif 'goto' in msg['type']:
                tar_az = msg['params']['azimuth']
                tar_el = msg['params']['elevation']
                msg['tar_az'] = tar_az
                msg['tar_az']
                self.send_msg(self.encoder.encode_set_tar_az(tar_az))
                self.send_msg(self.encoder.encode_set_tar_el(tar_el))
                if self.encoder.az_valid and self.encoder.el_valid:
                    self.send_msg(self.encoder.encode_goto_target_position())
            elif 'slew' in msg['type']:
                self.send_msg(self.encoder.encode_slew(msg['params']['dir']))
            elif msg['type']=='stop':
                self.send_msg(self.encoder.encode_stop_slew())
            elif msg['type'] == 'speed':
                self.send_msg(self.encoder.encode_set_slew_speed(msg['params']['speed']))
            elif msg['type'] == 'focus_speed':
                self.send_msg(self.encoder.encode_focus_speed(msg['params']['speed']))
            elif msg['type'] == 'focus_in':
                self.send_msg(self.encoder.encode_focus_inward())
            elif msg['type'] == 'focus_out':
                self.send_msg(self.encoder.encode_focus_outward())
            elif msg['type'] == 'focus_stop':
                self.send_msg(self.encoder.encode_focus_stop())
        except Exception as e:
            self.logger.info(sys.exc_info())
            pass


        self.dev_stat = self.encoder.get_status()
        self.dev_stat['type'] = 'RX'
        self.rx_q.put(self.dev_stat)





    #### Class Thread Handler ###########
    def get_tlm(self):
        ''' Called by Main Thread '''
        return self.tlm

    def stop(self):
        #self.conn.close()
        if self.conn: self._close_serial()
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
