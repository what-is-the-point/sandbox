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
from queue import Queue
from daemon.logger import *

from daemon.Autostar import *
from daemon import serial_thread


class Device_Thread(threading.Thread):
    def __init__(self, cfg, parent = None):
        threading.Thread.__init__(self, name=cfg['name'])
        self._stop  = threading.Event()
        self.cfg    = cfg
        # print(self.cfg)
        #self.logger = logger
        self.parent = parent
        self.logger = logging.getLogger(self.cfg['main_log'])
        self.logger.info("Initializing {:s} Device Thread for {:s} Protocol".format(self.cfg['type'],
                                                                           self.cfg['protocol']))

        self.connected = False
        self.tx_q = Queue() # Main_Thread -> Device
        self.rx_q = Queue() # Main_thread <- Device

        self._init_device()



    def _init_device(self):
        #Initialize connection method
        if self.cfg['connection']['type'] == 'serial':
            self.conn = serial_thread.Serial_Thread(self.cfg['connection'],
                                                    self.cfg['main_log'],
                                                    self)
            self.conn.daemon = True
            self.logger.info('Launching Device Connection Thread')
            self.conn.start() #non-blocking

        if self.cfg['protocol'] == 'autostar':
            self.encoder = Autostar()

        self.tlm = { #Thread control Telemetry message
            "type":"TLM", #Message Type: Thread Telemetry
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
            self._process_rx_q()
            if not self.tx_q.empty(): #Received Message from Main Thread
                msg = self.tx_q.get() #retrieve message from FIFO buffer
                self._process_device_command(msg)
            time.sleep(0.001)
            pass

    #----CONNECTION THREAD FUNCTIONS----------------------------
    def _process_rx_q(self):
        '''
        Processes Messages from the Device Connection Thread
        Message Types:
            - TLM : Thread telemetry messages, metadata
            - RX  : Raw data received over connection thread
        '''
        if not self.conn.rx_q.empty(): #Received Message from Net Thread
            msg = self.conn.rx_q.get() #retrieve message from FIFO buffer
            if   msg['type']=='TLM': self._process_conn_tlm_message(msg)
            elif msg['type']== 'RX': self._process_conn_rx_response(msg)

    def _process_conn_tlm_message(self, tlm):
        """
        Process Messages from the Serial Thread that are TELEMETRY
        These Messages indicate Thread status
        """
        self.logger.info("Received Connection Thread Telemetry Message: {:s}".format(json.dumps(tlm)))
        self.tlm=tlm

    def _process_conn_rx_response(self, msg):
        buff = bytearray.fromhex(msg['msg'])
        self.logger.debug("Received Focus Motor msg: {:s}".format(buff.hex()))

    def get_tlm(self):
        '''
        Called by Main Thread
        '''
        return self.tlm

    #----CONNECTION THREAD FUNCTIONS----------------------------





    #---- FOCUS MOTOR RESPONSE PROCESSING--------------------
    #---- FROM FOCUS MOTOR TO DAEMON--------------------
    def _set_mode(self, mode):
        self.FocusMotor['mode'] = mode
        self.dev_log.info("Set Device Thread Mode: {:s}".format(self.FocusMotor['mode']))

    def _decode_focus_motor_response(self, msg):
        buff = bytearray.fromhex(msg['msg'])
        self.logger.debug("Received device msg: {:s}".format(buff.hex()))
        decoded = None
        decoded = self.fm.decode(buff)

        if decoded is not None:
            decoded['datetime']=msg['datetime']
            self._update_focus_motor_state(decoded)
            # if decoded['type'] == "position":
            #     self.tlm['position'] = decoded['position']
            # elif decoded['type'] == "move_done":
            #     self.tlm['move_done'] = decoded['done']
            # elif decoded['type'] == "dev_version":
            #     self.tlm['version'] =  decoded['version']
            # elif decoded['type'] == 'backlash':
            #     self.tlm['backlash'] = decoded['backlash']

            # if decoded['type'] == "position":
            #     self.rx_q.put(decoded)

    def _update_focus_motor_state(self, decoded):
        self.FocusMotor['datetime'] = decoded['datetime']
        if decoded['type'] == "position":
            self.FocusMotor['position'] = decoded['position']
        elif decoded['type'] == "move_done":
            self.FocusMotor['move_done'] = decoded['done']
        elif decoded['type'] == "dev_version":
            self.FocusMotor['version'] =  decoded['version']
        elif decoded['type'] == 'backlash':
            self.FocusMotor['backlash'] = decoded['backlash']

        # if decoded['type'] == "position":
        #     self.rx_q.put(decoded)

        print(self.FocusMotor)

    #---- FROM FOCUS MOTOR TO DAEMON--------------------
    #---- END FOCUS MOTOR RESPONSE PROCESSING--------------------

    #---- FOCUS MOTOR COMMAND PROCESSING--------------------
    #---- FROM DAEMON TO Focus Motor--------------------
    def _process_device_command(self, msg):
        """
        Received Command From Main Thread Destined For device
        Format Raw Message
        Write to Connection Thread
        """
        # print(msg)
        self.logger.info("Received Device Command Plane Message: {:s}".format(json.dumps(msg)))
        if   "position" in msg['type']: raw = self.fm.encode_get_position()
        elif "stop" in msg['type']:
            raw = self.fm.encode_stop()
            self.SEQUENCE = "RUN"
            self.dev_log.info("Set State = {}".format(self.SEQUENCE))
        elif "slew" in msg['type']:     raw = self.fm.encode_slew(msg)
        elif "goto" in msg['type']:
            # raw = self.fm.encode_goto_position(msg['params']['position'])
            raw = None
            self._sequence_goto_position(msg['params']['position'])

        if raw is not None:
            self.last_type = msg['type']
            if self.connected:
                self.dev_log.warning("Sending: {:s}".format(msg['type']))
                cmd_dict = self._encode_conn_command(msg['type'], raw)
                self.conn.tx_q.put(cmd_dict)
        # else: self.dev_log.warning("Invalid Command Parameters")

    def _encode_conn_command(self, name="", raw=None):
        """
        Generates a Command Dictionary for the Connection Thread
        Parameters:
            name: the 'key' for the command
             hex: hexstring of the binary data to write to the device
        """
        cmd_dict={
            "type":"CMD",
            "cmd":"SEND",
            "msg": {
                "name": name,
                "hex":raw.hex()
            }
        }
        return cmd_dict
    #---- END Celestron Focus Motor COMMAND PROCESSING--------------------

    #### Class Thread Handler ###########
    def stop(self):
        #self.conn.close()
        self.logger.info('{:s} Terminating...'.format(self.name))
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
